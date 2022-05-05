// main cs algo which uses cs insertion algorithm in order to introduce charging stations in best paths generated using algo

#include<bits/stdc++.h>
#define inf 10000000

using namespace std; 

// file path dependencies
string graph_input_file = "input_graph.txt";
string query_input_file = "queries.txt";
string paths_output_file = "output_graph.txt";
string cs_paths_output_file = "cs_output_graph.txt";
string cs_input_file = "cs_input.txt";
string ev_info_file = "ev_info.txt";

// max nodes, edges, paths, number of cs
const int MAX_NODES = 100009;
const int max_paths = 100;
const int display_number_of_paths = 5;
const int MAX_CS = 10;
int N, M, Q, cnt, CS, ev_initial_charge, ev_capacity;

vector<pair<int,int> > graph[MAX_NODES];  // adjacency list for graph
vector<pair<int,vector<int> > > paths[MAX_NODES]; // stores best paths for queries
vector<pair<vector<int>,pair<double,pair<double,double>> > > final_paths[MAX_NODES];
vector<int> fail_reasons[MAX_NODES];
map<int, pair<int,vector<int> > > cs_paths[MAX_NODES];  // best cs paths for queries

map<pair<int,int>, int> edges;  // map of all edges
set<int> charging_stations; // set of all charging stations

// assuming 1 unit of travel burns lamda energy where Capacity is given
const double lambda_energy_spent = 0.1;
// assuming one unit charging takes charging_unit_time 
const double charging_unit_time = 0.1;
// assuming one unit of time travels ev_speed units distance
const double ev_speed = 5.0;

int fail_condition; // 0 if init charge is less 1 if capacity is less

// insert cs algo based on max_iterations parameter
pair<vector<int>,pair<double,pair<double,double>> > insert_charging_stations(vector<int> &path){
    vector<int> processed(path.size(),0);
    int max_iterations = 20;
    set<pair<double,pair<pair<double,double>,pair<int,int> > > > st;
    st.insert({0.0,{{ev_initial_charge,0},{0,-1}}});
    pair<double,pair<pair<double,double>,pair<int,int> > >  ans = {0,{{0,0},{-1,-1}}};
    map<pair<double,pair<pair<double,double>,pair<int,int> > >, pair<double,pair<pair<double,double>,pair<int,int> > > > parent;
    while(!st.empty()){
        auto element = *st.begin();
        st.erase(st.begin());
        double el_time = element.first;
        double el_energy = element.second.first.first;
        int el_node = element.second.second.first;
        int el_parent = element.second.second.second;
        double charging_time = element.second.first.second;

        if(el_node == path.size()-1){
            ans = element;
            break;
        }

        if(processed[el_node]>max_iterations)continue;
        processed[el_node]++;

        double energy_taken = lambda_energy_spent*edges[{path[el_node],path[el_node+1]}];
        double time_taken = edges[{path[el_node],path[el_node+1]}]/ev_speed;
        double total_time = time_taken + el_time;
        double total_energy = el_energy - energy_taken;
        if(total_energy > 0){
            parent[{total_time,{{total_energy, charging_time},{el_node+1,-1}}}] = element;
            st.insert({total_time,{{total_energy, charging_time},{el_node+1,-1}}});
        }

        for(auto cs:charging_stations){
            time_taken = 0;
            energy_taken = lambda_energy_spent*cs_paths[path[el_node]][cs].first;
            if(energy_taken>el_energy){
                continue;
            }
            fail_condition = 1;
            time_taken += (ev_capacity-(el_energy-energy_taken))*charging_unit_time; // charging time
            double total_charging_time = charging_time + time_taken;
            time_taken += cs_paths[path[el_node]][cs].first/ev_speed;    //node to cs
            int dist = 1000000000;
            int jump_node = el_node+1;
            for(int node = el_node+1; node<min((int)path.size(),el_node+10);node++){
                if(cs_paths[path[node]][cs].first < dist){
                    jump_node = node;
                    dist = cs_paths[path[node]][cs].first;
                }
            }
            time_taken += cs_paths[path[jump_node]][cs].first/ev_speed; // cs to next node
            energy_taken = lambda_energy_spent*cs_paths[path[jump_node]][cs].first; // energy to reach node from cs
            total_energy = ev_capacity - energy_taken; // total energy
            total_time = el_time + time_taken; // total time
            if(total_energy > 0){
                parent[{total_time,{{total_energy, total_charging_time},{jump_node,cs}}}] = element;
                st.insert({total_time,{{total_energy, total_charging_time},{jump_node,cs}}});
            }
        }
    }

    // extracting paths
    vector<int> output_path;
    double total_energy_taken = 0;
    double total_time_taken = ans.first;
    double total_charging_time = ans.second.first.second;
    while(ans.second.second.first!=-1){
        int el_node = ans.second.second.first;
        int cs = ans.second.second.second;
        if(output_path.empty() || output_path.back()!=path[el_node])
            output_path.push_back(path[el_node]);
        if(el_node==0)break;
        if(cs!=-1){
            for(int i=cs_paths[path[el_node]][cs].second.size()-2;i>0;i--){
                output_path.push_back(cs_paths[path[el_node]][cs].second[i]);
                int node1 = cs_paths[path[el_node]][cs].second[i];
                int node2 = cs_paths[path[el_node]][cs].second[i+1];
                total_energy_taken += edges[{node1,node2}]*lambda_energy_spent;
            }
            for(int i=0;i<cs_paths[path[el_node-1]][cs].second.size()-1;i++){
                output_path.push_back(cs_paths[path[el_node]][cs].second[i]);
                int node1 = cs_paths[path[el_node]][cs].second[i];
                int node2 = cs_paths[path[el_node]][cs].second[i+1];
                total_energy_taken += edges[{node1,node2}]*lambda_energy_spent;
            }
        }else{
            total_energy_taken += edges[{path[el_node],path[el_node-1]}]*lambda_energy_spent;
        }
        ans = parent[ans];
    }
    reverse(output_path.begin(),output_path.end());
    return {output_path,{total_time_taken,{total_energy_taken, total_charging_time}}};

}

// beam search algorithm to maintain best paths 
// takes a distance vector based on dijsktra algorithm and finds max best paths
vector<pair<int,vector<int> > > beam_search(int src,int dst, vector<int> &distance){
    set<pair<int,pair<int,vector<int> > > > st;
    vector<int> temp;
    temp.push_back(dst);
    st.insert({distance[dst],{0,temp}});
    vector<pair<int,vector<int> > > ans;
    while(ans.size()<max_paths && !st.empty()){
        auto element = *st.begin();
        st.erase(st.begin());
        int dist = element.second.first;
        vector<int> path = element.second.second;
        int node = path.back();
        if(node==src){
            reverse(path.begin(),path.end());
            ans.push_back({dist,path});
            continue;
        }
        for(auto el:graph[node]){
            if(distance[el.first]>distance[node])continue;

            path.push_back(el.first);
            st.insert({distance[el.first]+dist,{dist+el.second,path}});
            path.pop_back();
        }
        while(st.size()>max_paths){
            auto it = st.end();
            it--;
            st.erase(it);
        }
    }
    return ans;
}

// dijkstra algorithm to generate distance vector
vector<pair<int,vector<int> > > dijkstra(int src, int dst){
    vector<int> distance(N+1,inf);
    vector<int> parent(N+1,-1);

    set<pair<int,int> > st;
    st.insert({0,src});
    distance[src] = 0;
    while(!st.empty()){
        auto element = *(st.begin());
        st.erase(st.begin());
        int dist = element.first;
        int node = element.second;
        if(distance[node]!=dist)continue;
        if(node == dst) break;
        for(auto el:graph[node]){
            if(distance[el.first] > dist + el.second){
                parent[el.first] = node;
                distance[el.first] = dist + el.second;
                st.insert({distance[el.first],el.first});
            }
        }
    }

    return beam_search(src,dst,distance);
    
}
int main(){
    cnt = 0;

    // initialising file pointers
    fstream graph_reader, query_reader, query_printer, cs_query_printer, cs_reader, ev_info_reader;
    graph_reader.open(graph_input_file);
    query_reader.open(query_input_file);
    cs_reader.open(cs_input_file);
    ev_info_reader.open(ev_info_file);
    cs_query_printer.open(cs_paths_output_file,ios::trunc | ios::out | ios::in);
    query_printer.open(paths_output_file,ios::trunc | ios::out | ios::in);
    graph_reader >> N;
    graph_reader >> M;
    query_reader >> Q;
    cs_reader >> CS;
    ev_info_reader >> ev_initial_charge >> ev_capacity;

    cout<<N<<" "<<M<<" "<<Q<<" "<<CS<<endl;

    // taking graph input
    for(int i=0;i<M;i++){
        int x,y,z;
        graph_reader >> x >> y >> z;
        graph[x].push_back({y,z});
        graph[y].push_back({x,z});

        if(edges.find({x,y})!=edges.end()){
            edges[{x,y}] = min(edges[{x,y}],z);
        }else{
            edges[{x,y}] = z;
        }

        if(edges.find({y,x})!=edges.end()){
            edges[{y,x}] = min(edges[{y,x}],z);
        }else{
            edges[{y,x}] = z;
        }
    }

    //  taking cs input
    for(int i=0;i<CS;i++){
        int cs;
        cs_reader >> cs;
        charging_stations.insert(cs);
        //  finding best path of each node from each cs using dijkstra
        for(int node = 0;node < N; node++){
            vector<pair<int,vector<int> > > temp = dijkstra(cs, node); 
            cs_paths[node][cs] = temp[0];
        }
    }

    // taking query input
    for(int i=0;i<Q;i++){
        int src, dst;
        query_reader >> src >> dst;
        auto temp = dijkstra(src, dst);
        auto temp1 = temp;
        temp1.clear();
        int dif = (temp.size() + display_number_of_paths -1)/display_number_of_paths;
        for(int i=0;i<temp.size();i+=dif){
            temp1.push_back(temp[i]);
        }
        if(temp1.back()!=temp.back()){
            temp1.push_back(temp.back());
        }
        paths[i] = temp1;
        
    }


    // running cs insertion for each best path
    for(int i=0;i<Q;i++){
        vector<pair<vector<int>,pair<double,pair<double,double>> > > temp;
        vector<int> temp1;
        for(auto el:paths[i]){
            fail_condition = 0;
            temp.push_back(insert_charging_stations(el.second));
            temp1.push_back(fail_condition);
        }
        final_paths[i] = temp;
        fail_reasons[i] = temp1;
    }

    // printing best shortest paths results
    query_printer << Q << endl;

    for(int i=0;i<Q;i++){
        query_printer << paths[i].size() << endl;
        for(auto el:paths[i]){

            query_printer << el.second.size() << " " << el.first << endl;
            for(auto nodes:el.second){
                query_printer << nodes << " "; 
            }
            query_printer << endl ;

        }
        
    }

    // printing results based on cs
    cs_query_printer << Q << endl;

    for(int i=0;i<Q;i++){
        cs_query_printer << final_paths[i].size() << endl; 
        for(auto el:final_paths[i]){
            cs_query_printer << el.first.size() << " " << el.second.first << " " << el.second.second.first << " " << el.second.second.second << endl;
            if(el.first.empty())cs_query_printer << fail_reasons[i][0];
            for(auto nodes:el.first){
                cs_query_printer << nodes << " ";
            }
            cs_query_printer << endl;
        }
    }

    // closing file pointers.
    graph_reader.close();
    query_reader.close();
    query_printer.close();
    cs_reader.close();
    ev_info_reader.close();



}