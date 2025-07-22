from neo4j import GraphDatabase

class Interface:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

    def bfs(self, start_node, last_node):
        # TODO: Implement this method
        
        query1 ="""
                    CALL gds.graph.project(
                    'BFS',
                     {
                        TRIP: {
                        properties: 'distance'
                        }
                    }
                    )
        """
        query2 = f"""
            MATCH (pickup:Location {{name: {start_node}}}), (dropoff:Location {{name: {last_node}}})
            WITH id(pickup) AS pk, id(dropoff) AS df
            CALL gds.bfs.stream(
                'BFS', {{
                    sourceNode: pk,
                    targetNodes: [df]
                }}
            ) 
            YIELD path
            RETURN path
        """
        with self._driver.session() as session:
            pro =session.run(query1)
            data = session.run(query2) 
            data = list(data) 
        print("data",data)
        bfs_dict=[]
        for record in data:
            print("record",record)
            bfs_dict.append(record)
                # bfs_dict.append({"name": int(record["name"])})
        print("bfs_dict",bfs_dict)
        parsed_path = [{"name": int(node["name"])} for node in bfs_dict[0]['path'].nodes]  # Extracts node names along path
        return [{"path": parsed_path}]
        # parsed_path = [{"name": node["name"]} for node in data if "name" in node]
        # return parsed_path

    def pagerank(self, max_iterations, weight_property):
        # TODO: Implement this method
        query1 = f"""
        CALL gds.graph.project(
            'PageRank',
            'Location',  // Node label
            {{
                TRIP: {{
                    properties: '{weight_property}'
                }}
            }}
        );
    """
    
        # Query to get the node with the highest PageRank score
        query2 = f"""
            CALL gds.pageRank.stream(
                'PageRank',
                {{maxIterations: {max_iterations}, relationshipWeightProperty: '{weight_property}'}}
            )
            YIELD nodeId, score
            WITH nodeId, score
            ORDER BY score DESC
            LIMIT 1
            MATCH (n) WHERE id(n) = nodeId
            RETURN n.name AS name, score
        """
        
        # Query to get the node with the lowest PageRank score
        query3 = f"""
            CALL gds.pageRank.stream(
                'PageRank',
                {{maxIterations: {max_iterations}, relationshipWeightProperty: '{weight_property}' }}
            )
            YIELD nodeId, score
            WITH nodeId, score
            ORDER BY score ASC
            LIMIT 1
            MATCH (n) WHERE id(n) = nodeId
            RETURN n.name AS name, score
        """
        with self._driver.session() as session:
            project= session.run(query1)
            max_val = session.run(query2) 
            min_val = session.run(query3)
            pagerank_result=[max_val,min_val]
            pagerank_dict = []
            for i in range(len(pagerank_result)):
                for record in pagerank_result[i]:
                    pagerank_dict.append({"name": int(record["name"]), "score": record["score"]})

            # print(max_val,min_val)
        return pagerank_dict

