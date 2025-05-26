"""
Evaluator for the function minimization example
"""
import subprocess
import json
import networkx as nx
import sys


# Define graph constructors
def has_book(G, num_nodes):
    num_pages = num_nodes - 2  # Book graph B<n> has n-2 pages
    # A book is num_pages triangles sharing a common edge
    for u, v in G.edges:
        common_neighbors = set(G.neighbors(u)).intersection(G.neighbors(v))
        if len(common_neighbors) >= num_pages:
            return True
    return False


def has_clique(G, num_nodes):
    for clique in nx.find_cliques(G):
        if len(clique) >= num_nodes:
            return True
    return False


def contains_subgraph(col_graph, target_spec):
    """Check if col_graph contains target as subgraph."""
    t, n = target_spec[0], int(target_spec[1:])
    if t == 'K':
        return has_clique(col_graph, n)
    elif t == 'B':
        return has_book(col_graph, n)


def run_with_timeout(program_path, program_args, timeout_seconds):
    """
    Run a program with a timeout using subprocess.
    """
    try:
        result = subprocess.run(
            ['python', program_path, *program_args],
            timeout=timeout_seconds,
            capture_output=True,
            text=True
        )
        return result.stdout
    except subprocess.TimeoutExpired as e:
        return None


def run_on_graphs(program_path, graph1, graph2, timeout_seconds):
    """
    Run the program on two graphs with a timeout.

    Args:
        program_path: Path to the program file
        graph1: First graph in JSON format
        graph2: Second graph in JSON format
        timeout_seconds: Timeout in seconds

    Returns:
        The output of the program or None if it times out
    """
    try:
        result = subprocess.run(
            [sys.executable, program_path, graph1, graph2, str(timeout_seconds)],
            timeout=timeout_seconds + 1,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error running program: {result.stderr}")
            return None
        # print(repr(result.stdout))  # Debugging output
        try:
            output_dict = json.loads(result.stdout)
        except json.JSONDecodeError:
            print('Error decoding JSON output')
            return None
        if 'size' not in output_dict or 'edges' not in output_dict \
                or not isinstance(output_dict['edges'], list) \
                or not all(isinstance(edge, list) and len(edge) == 2 for edge in output_dict['edges']) \
                or not isinstance(output_dict['size'], int):
            print('Invalid output format')
            return None
        size = output_dict['size']
        for u, v in output_dict['edges']:
            if u >= size or v >= size or u < 0 or v < 0:
                print(f'Invalid edge ({u}, {v}) in output')
                return None
        return output_dict
    except subprocess.TimeoutExpired:
        print(f"Program timed out after {timeout_seconds} seconds")
        return None


def dict_to_graphs(graph_dict):
    size = graph_dict['size']
    red_graph = nx.from_edgelist(graph_dict['edges'])
    blue_graph = nx.Graph()
    blue_graph.add_nodes_from(range(size))
    blue_graph.add_edges_from(
        (u, v) for u in range(size) for v in range(size) if u < v and (u, v) not in red_graph.edges()
    )
    return red_graph, blue_graph


def evaluate(program_path):
    """
    Evaluate the program by running it multiple times and checking the size of the found graph.

    Args:
        program_path: Path to the program file

    Returns:
        Dictionary of metrics
    """
    # quick check on K3, K3
    result_dict = run_on_graphs(program_path, 'K3', 'K3', 10.5)
    if result_dict is None:
        return {'score': -1000}
    red, blue = dict_to_graphs(result_dict)
    if any(nx.triangles(red).values()) or any(nx.triangles(blue).values()):
        return {'score': -1000}
    if result_dict['size'] < 5:
        return {'score': -900}  # Better than nothing, but not great
    
    # naive socring: sum of found edges on some cases
    cases = [
        ('K4', 'K4'),  # Known Ramsey number R(4, 4) = 18, so should be 17
        ('B2', 'B2'),  # Known Ramsey number R(2, 2) = 12, so should be 11
        ('B10', 'K2'),  # Simple to show it's 9
        ('B6', 'B9')  # SOTA: 22, upper bound: 23
    ]
    score_dict = {}
    for i, (G1, G2) in enumerate(cases):
        result_dict = run_on_graphs(program_path, G1, G2, 5)
        if result_dict is None:
            return {'score': -1000}
        red, blue = dict_to_graphs(result_dict)
        if contains_subgraph(red, G1) or contains_subgraph(blue, G2):
            return {'score': -1000}
        score_dict[f'score_{i}'] = result_dict['size']
    score_dict['score'] = sum(score_dict.values())
    return score_dict


def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python evaluator.py <program_path>")
        sys.exit(1)
    
    program_path = sys.argv[1]
    metrics = evaluate(program_path)
    print(json.dumps(metrics))

if __name__ == "__main__":
    main()
