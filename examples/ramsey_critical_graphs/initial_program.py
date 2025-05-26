"""
Initial program for Ramsey critical graphs search.
created by chatGPT.
"""
import sys
import itertools
import networkx as nx
import time
import json


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
    else:
        raise ValueError(f"Unknown graph type: {t}. Expected 'K' or 'B'.")


# EVOLVE-BLOCK-START
def search_coloring(n, spec_red, spec_blue, start_time, timeout):
    """
    Greedy depth-first search for a 2-coloring of K_n edges avoiding spec_red in red and spec_blue in blue.
    """
    nodes = list(range(n))
    edges = list(itertools.combinations(nodes, 2))
    red_edges = set()

    # START: depth-first greedy with timeout check
    def backtrack(idx):
        if timeout is not None and (time.time() - start_time) > timeout:
            raise TimeoutError
        if idx == len(edges):
            return True
        u, v = edges[idx]
        # balance colors
        red_count = len(red_edges)
        blue_count = idx - red_count
        order = ['red', 'blue'] if red_count <= blue_count else ['blue', 'red']
        for color in order:
            if color == 'red':
                red_edges.add((u, v))
            # build partial graphs
            R = nx.Graph(); B = nx.Graph()
            R.add_nodes_from(nodes); B.add_nodes_from(nodes)
            for e in edges[:idx+1]:
                if e in red_edges:
                    R.add_edge(*e)
                else:
                    B.add_edge(*e)
            if timeout is not None and (time.time() - start_time) > timeout:
                raise TimeoutError
            if not contains_subgraph(R, spec_red) and not contains_subgraph(B, spec_blue):
                if backtrack(idx+1):
                    return True
            if color == 'red':
                red_edges.remove((u, v))
        return False
    # END: depth-first greedy with timeout check

    try:
        if backtrack(0):
            return red_edges
    except TimeoutError:
        raise
    return None


def iterative_search(spec1, spec2, timeout=None):
    n = 2
    start_time = time.time()
    best_sol = None
    best_n = 0

    while True:
        try:
            sol = search_coloring(n, spec1, spec2, start_time, timeout)
            if sol is not None:
                best_n = n
                best_sol = sol.copy()
            else:
                break
            n += 1
        except TimeoutError:
            return best_sol, best_n
    return best_sol, best_n
# EVOLVE-BLOCK-END


def main():
    if len(sys.argv) not in (3, 4):
        print("Usage: python ramsey_search.py <G_spec> <H_spec> [timeout_seconds]")
        sys.exit(1)
    spec1, spec2 = sys.argv[1], sys.argv[2]
    timeout = float(sys.argv[3]) if len(sys.argv) == 4 else None

    result, result_n = iterative_search(spec1, spec2, timeout)
    if result is not None:
        print(json.dumps({
            "size": result_n,
            "edges": list(result),
        }))
    else:
        print(json.dumps({
            "size": 1,
            "edges": [],
        }))


if __name__ == '__main__':
    main()
