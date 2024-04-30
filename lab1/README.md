# Lab 1 - Set Covering

This solution has been developed in collaboration with my colleague Andrea D'Attila (303339).

For the solution a greedy algorithm has been adopted.

The results obtained by this greedy algorithm could be used to implement an optimized version of the breadth-first search algorithm: a node should not be processed if its cost is greater than the cost obtained with the greedy solution, because, for sure, it leads to a worse solution.

In order to explain the algorithm, we will consider an example of problem with `N = 10` and `seed = 42`.

This is the list of lists which is generated in this example.

[[0, 4], [1, 2, 3], [9, 6], [0, 1], [8, 9, 3], [8, 3], [0, 3, 4, 7, 9], [4, 5, 6], [1, 3, 5], [1, 6], [0, 9, 4, 5], [8, 1, 6], [9, 3, 5], [0, 3], [1, 3, 6], [2, 5, 7], [1, 3, 4, 9], [8, 2, 3], [3, 4, 5, 6, 8], [0, 3], [1, 3, 4, 6], [3, 6, 7], [2, 3, 4], [9, 6], [8, 2, 3, 7], [0, 1], [9, 2, 6], [6], [8, 0, 4, 1], [1, 4, 5, 6], [0, 4, 7], [8, 1, 4], [2, 5], [9, 5], [0, 1, 3, 4, 5], [9, 3], [1, 7], [8, 2], [8, 2, 7], [8, 9, 3, 6], [4, 5, 6], [8, 1, 3, 7], [0, 5], [0, 9, 3], [0, 3], [0, 5], [8, 3], [8, 2, 3, 7], [1, 3, 6, 7], [5, 6]]

---

After generating the problem, the algorithm will **sort** the lists by length, in descending order (i.e. from longest to shortest).

[**[0, 3, 4, 7, 9]**, [3, 4, 5, 6, 8], [0, 1, 3, 4, 5], [0, 9, 4, 5], [1, 3, 4, 9], [1, 3, 4, 6], [8, 2, 3, 7], [8, 0, 4, 1], [1, 4, 5, 6], [8, 9, 3, 6], [8, 1, 3, 7], [8, 2, 3, 7], [1, 3, 6, 7], [1, 2, 3], [8, 9, 3], [4, 5, 6], [1, 3, 5], [8, 1, 6], [9, 3, 5], [1, 3, 6], [2, 5, 7], [8, 2, 3], [3, 6, 7], [2, 3, 4], [9, 2, 6], [0, 4, 7], [8, 1, 4], [8, 2, 7], [4, 5, 6], [0, 9, 3], [0, 4], [9, 6], [0, 1], [8, 3], [1, 6], [0, 3], [0, 3], [9, 6], [0, 1], [2, 5], [9, 5], [9, 3], [1, 7], [8, 2], [0, 5], [0, 3], [0, 5], [8, 3], [5, 6], [6]]

---

The algorithm is starting by picking the longest list as a starting point (i.e. the first list in the ordered list of lists).

At this point the solution is `sol = [0, 3, 4, 7, 9]`. From now on, the algorithm will look for the most promising lists to add. 

This is done by using the following heuristic function `h(x)`. For each list `x` in the problem set we compute:
- **common elements** between `x` and `sol`
- **new elements** that are present in `x` but not in `sol`

$$ cost(x) = \frac{common\quad elements}{new\quad elements}$$

Then, the `x` corresponding to the minimum cost will be added to the solution set.

In case of two elements that have same cost, the longest one is taken (i.e. the first one that appears in the ordered list of lists).

![Example](./Example%20with%20N%20%3D%2010.png)

In the example provided with `N = 10` and `seed = 42`, the greedy algorithm will give an **optimal** solution, with minimum `w = 10` (i.e. 10 elements contained in total):

[[0, 3, 4, 7, 9], [8, 1, 6], [2, 5]]

This is the output for $N \in [5, 10, 20, 100, 500, 1000]$

- Greedy solution for `N=5   : w=5` (bloat=0%) - **optimal**
- Greedy solution for `N=10  : w=10`  (bloat=0%) - **optimal**
- Greedy solution for `N=20  : w=24` (bloat=20%)
- Greedy solution for `N=100 : w=182` (bloat=82%)
- Greedy solution for `N=500 : w=1262` (bloat=152%)