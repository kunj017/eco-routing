#include<bits/stdc++.h>
#define inf 10000000

using namespace std; 

string graph_input_file = "input_graph.txt";
string query_input_file = "queries.txt";
string paths_output_file = "output_graph.txt";
const int MAX_NODES = 100009;
int N, M,Q,cnt ;
vector<pair<int,int> > graph[MAX_NODES];
vector<int> paths[MAX_NODES];


vector<int> dijkstra(int src, int dst){
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

    vector<int> ans;
    int node = dst;
    while(node != -1){
        ans.push_back(node);
        node = parent[node];
    }
    reverse(ans.begin(),ans.end());
    return ans;
}
int main(){
    cnt = 0;
    fstream graph_reader, query_reader, query_printer;
    graph_reader.open(graph_input_file);
    query_reader.open(query_input_file);
    query_printer.open(paths_output_file,ios::trunc | ios::out | ios::in);
    graph_reader >> N;
    graph_reader >> M;
    query_reader >> Q;

    cout<<N<<" "<<M<<" "<<Q<<endl;;

    for(int i=0;i<M;i++){
        int x,y,z;
        graph_reader >> x >> y >> z;
        graph[x].push_back({y,z});
        graph[y].push_back({x,z});
    }

    for(int i=0;i<Q;i++){
        int src, dst;
        query_reader >> src >> dst;
        paths[i] = dijkstra(src, dst);
    }

    query_printer << Q << endl;

    for(int i=0;i<Q;i++){
        query_printer << paths[i].size() << endl;
        for(auto el:paths[i]){
            query_printer << el << " ";
        }
        query_printer << endl ;
    }

    graph_reader.close();
    query_reader.close();
    query_printer.close();



}