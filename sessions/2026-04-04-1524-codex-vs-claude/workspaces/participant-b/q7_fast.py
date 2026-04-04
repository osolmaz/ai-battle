# The brute force approach is too slow for n=40. 
# Let me use a smarter approach.
#
# Key insight: We can decompose the problem using the structure of the 
# divisibility poset. Elements can be processed in a specific order, and
# the state can be compressed.
#
# Approach: Think of it as scheduling elements level by level.
# 
# Actually, let me try a different approach: process elements by removing
# maximal elements, and use the complement approach.
#
# The number of linear extensions L(P) of a poset P satisfies:
# L(P) = sum over maximal elements m of L(P \ {m})
#
# And L(P) = |P|! / |P| * (average over maximal elements of L(P\{m}))
# which doesn't help directly.
#
# But we can use the identity:
# L(P) / |P|! = sum_{m maximal} L(P\{m}) / (|P|-1)! * (1/|P|) ... no.
#
# Actually: L(P) = sum_{m maximal} L(P \ {m})
# This is because a linear extension ends with some maximal element m.
#
# So we can compute L(P) by removing maximal elements one at a time.
# The state is the current set of elements. We need to track which subsets
# of {1,...,40} arise as order ideals of the complement.
#
# The elements of {1,...,40} that are NOT maximal are {1,...,20}.
# The maximal elements are {21,...,40}.
#
# When we remove a maximal element, the remaining set is still a "downward
# closed" set minus some maximal elements. The state can be encoded by
# which of the maximal elements {21,...,40} remain (those not yet removed).
# But we also need to track which non-maximal elements have been "freed"
# by removing elements above them.
#
# Hmm, actually every element in {1,...,20} is NOT maximal (since 2x ≤ 40),
# so they'll never be "removed from the top". They'll only become available
# when everything above them is gone... wait, no. In the downward approach,
# we remove from the top. So we first remove elements from {21,...,40},
# then elements from {11,...,20} become maximal, etc.
#
# The set of remaining elements at any point is a downward-closed set 
# (order ideal) of the divisibility poset on {1,...,40}.
# 
# An order ideal is determined by its set of maximal elements (antichain).
# The number of antichains/order ideals might be manageable.
#
# Actually, for the divisibility poset on {1,...,40}, the number of order
# ideals could be large. Let me estimate.
#
# Alternative approach: notice that elements with "large" prime factors are
# relatively independent. Let me decompose by prime support.
#
# Group elements by their largest prime factor:
# Largest prime 2: {2, 4, 8, 16, 32}
# Largest prime 3: {3, 9, 27, 6, 12, 18, 24, 36}
# Largest prime 5: {5, 25, 10, 15, 20, 30, 40}
# Largest prime 7: {7, 14, 21, 28, 35}
# Largest prime 11: {11, 22, 33}
# Largest prime 13: {13, 26, 39}
# Largest prime 17: {17, 34}
# Largest prime 19: {19, 38}
# Largest prime 23: {23}
# Largest prime 29: {29}
# Largest prime 31: {31}
# Largest prime 37: {37}
#
# Hmm, but elements in different groups can still be related by divisibility
# (e.g., 6 = 2*3 is in the "largest prime 3" group but 2 is in a different
# group). The issue is that the groups overlap in their dependencies.
#
# OK let me try a completely different approach. 
# I'll use the "width" decomposition or chain decomposition.
#
# Actually, let me try to compute this using a more efficient DP.
# Instead of tracking the full set, I'll track which elements are "available"
# (ready to be placed). The available set changes as elements are placed.
#
# At any point, the available elements are exactly those whose proper 
# divisors (in {1,...,40}) have ALL been placed. This is the "antichain of
# minimal unplaced elements" concept.
#
# The state can be represented more compactly if I note that:
# - Placing an element x only affects the availability of multiples of x.
# - Two placements that result in the same set of placed elements lead to
#   the same future, regardless of order.
#
# So the state is the set of placed elements, which is an order ideal.
# And the DP counts: for each order ideal I, the number of linear extensions
# of the induced poset on I.
#
# This is still exponential in the worst case, but for the divisibility 
# poset, the number of order ideals might be manageable.
#
# Let me compute the number of order ideals of the divisibility poset on {1,...,40}.
# An order ideal I ⊂ {1,...,40} satisfies: if x ∈ I and y|x with y ∈ {1,...,40}, then y ∈ I.
#
# Equivalently, I is determined by choosing, for each maximal chain, a cutoff.
# But the chains overlap, so it's more complex.
#
# Let me try to enumerate order ideals using a different decomposition.
# Elements can be processed in order: first decide about 1, then 2, then 3, etc.
# But the constraint is: if x ∈ I, then all divisors of x in {1,...,40} must be in I.
# Equivalently: if x ∉ I, then all multiples of x in {1,...,40} must be ∉ I.
#
# Processing elements from 1 to 40:
# - 1: must be in I (since 1 is in every order ideal that's nonempty... 
#   well, the empty set is also an order ideal, but in our problem we place all 40 elements).
#
# Actually, in our problem, every element IS placed (we're permuting all of {1,...,40}).
# The order ideal is the set of elements placed so far at any intermediate step.
# The DP counts: for each order ideal I, the number of linear extensions of the
# elements in I (i.e., how many ways to place the elements of I in order respecting
# the divisibility constraints).
#
# The full answer is L({1,...,40}) = the value for the full set.
#
# OK I think the right approach is just the standard DP on order ideals.
# Let me estimate the number of order ideals of the divisibility lattice on {1,...,40}.
#
# For each number 1-40, we can represent it by its prime factorization.
# The divisibility poset is a sub-poset of the product of chains:
# C_5 × C_3 × C_2 × C_1 × ... (for primes 2, 3, 5, 7, ...)
# where C_k has k+1 elements (exponents 0 through k).
#
# An order ideal of the full product poset would have 
# 6 * 4 * 3 * 2^8 = 72 * 256 = 18432 order ideals (for a product of chains).
# But our poset is a sub-poset, so there might be more or fewer.
#
# Actually, for the PRODUCT of chains C_{a_1} × ... × C_{a_k}, the number
# of order ideals is (a_1+1)(a_2+1)...(a_k+1). But our poset is NOT a product;
# it's a sub-poset restricted to elements with N(x) ≤ 40.
#
# I think the number of order ideals could be in the millions for n=40,
# which might be manageable with memoization.
#
# Let me try a different encoding. Instead of tracking the full order ideal,
# I'll track the "profile": for each prime, the maximum exponent of that prime
# among the placed elements. But this doesn't fully determine the order ideal
# because, e.g., having placed 12 = 2^2 * 3 doesn't mean both 4 = 2^2 and 
# 3 are placed.
#
# Hmm, actually, if we place elements in a valid topological order, then
# placing 12 means 1, 2, 3, 4, 6 are all already placed (since they're all
# proper divisors of 12 in {1,...,40}).
#
# So an order ideal IS determined by: which numbers in {1,...,40} are included,
# subject to the constraint that all divisors are included.
#
# Let me try to enumerate order ideals more carefully.
# 
# Actually, I think the right approach for a computational contest is to:
# 1. Model this as a DAG (Hasse diagram of divisibility)
# 2. Count topological sorts using the DP with bitmask over a suitable 
#    decomposition
#
# For 40 elements, direct bitmask DP is impossible (2^40 states).
# But we can use the fact that many elements are "independent" and 
# combine results using multinomial coefficients.
#
# The independent groups:
# After removing element 1 (which must be first), the remaining elements
# form several "independent" components in the Hasse diagram. Wait, are they 
# truly independent?
#
# In the Hasse diagram, an edge a→b means a is a proper divisor of b and
# there's no c with a|c|b. But for counting linear extensions, we need the 
# full divisibility relation, not just the Hasse diagram.
#
# Two elements are "related" if one divides the other. Two elements are 
# "independent" if they're incomparable.
#
# For the linear extensions count, we can decompose into connected components
# of the comparability graph and then interleave using multinomial coefficients.
#
# The comparability graph on {2,...,40}: vertices are connected if one divides
# the other. Let me find connected components.
#
# Component analysis:
# Start from 2: 2 is comparable to 4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40
# From 4: comparable to 8,12,16,20,24,28,32,36,40
# From 3: comparable to 6,9,12,15,18,21,24,27,30,33,36,39
# 2 and 3 are NOT directly comparable, but both are comparable to 6.
# In the comparability graph, 2-6-3 is a path, so they're in the same component.
# Similarly, 5 is comparable to 10,15,20,25,30,35,40.
# 5 and 2 are not comparable, but 5-10-2, so same component.
# 7 is comparable to 14,21,28,35.
# 7 and 2: 7-14-2, same component.
# 11-22-2, same component.
# 13-26-2, same component.
# 17-34-2, same component.
# 19-38-2, same component.
#
# So all elements except 23, 29, 31, 37 are in one connected component.
# 23, 29, 31, 37 are isolated (comparable only to 1, which is placed first).
#
# Wait, but this is the comparability graph, not the Hasse diagram.
# For linear extensions, what matters is: if two elements x,y are incomparable
# (neither divides the other), they can be placed in either order relative
# to each other.
#
# If we have independent components C_1, ..., C_k with sizes n_1, ..., n_k
# and L_1, ..., L_k linear extensions respectively, then the total number
# of linear extensions is:
# (n_1 + ... + n_k)! / (n_1! * ... * n_k!) * L_1 * ... * L_k
# = multinomial(n_1,...,n_k) * product of L_i
#
# But components are "independent" only if NO element in C_i is comparable
# to any element in C_j. For the comparability graph, this means the 
# components are the connected components.
#
# We have:
# - One big component with 35 elements (all non-isolated elements of {2,...,40})
# - 4 isolated elements: 23, 29, 31, 37
#
# Each isolated element forms a component of size 1 with L = 1.
# The big component has 35 elements with some number L of linear extensions.
#
# Total linear extensions of {2,...,40} = 39! / (35! * 1! * 1! * 1! * 1!) * L * 1 * 1 * 1 * 1
# = C(39, 35, 1, 1, 1, 1) * L
# = 39! / (35! * 1! * 1! * 1! * 1!) * L
# = (39 * 38 * 37 * 36) * L
# Wait, 39!/(35! * 1^4) = 39*38*37*36 = 2193360? Hmm, actually:
# 39!/35! = 39*38*37*36 = 39*38*37*36

# Hmm but actually we should divide by the product of factorials of component sizes.
# The multinomial coefficient for interleaving components of sizes 35, 1, 1, 1, 1 is:
# 39! / (35! * 1! * 1! * 1! * 1!) = 39! / 35! = 39 * 38 * 37 * 36

# And the total answer for {1,...,40} is 1 * [linear extensions of {2,...,40}]
# since 1 must be first.
# = (39 * 38 * 37 * 36) * L

# But wait, I forgot that the 4! for ordering the 4 isolated elements is 
# already included in the multinomial. Each isolated component has L_i = 1,
# and the multinomial counts the number of ways to interleave them.

# So the answer = (39*38*37*36) * L
# where L is the number of linear extensions of the big component of 35 elements.

# Now I need to compute L for the big component. This is still hard.
# Let me try to further decompose the big component.

# Actually, wait. Let me reconsider. Within the big component, there might
# be sub-structures that allow decomposition.

# The big component consists of {2,...,40} \ {23,29,31,37}.
# Let me look at the "independent" sub-groups within this component.

# Elements with only small prime factors form dense substructures.
# Elements like 11, 22, 33: 11 is comparable to 22 and 33 only.
# 22 = 2*11 is also comparable to 2.
# 33 = 3*11 is also comparable to 3.
# So 11, 22, 33 are connected to the rest of the big component.
# They're NOT independent.

# I think the big component is truly one connected component with lots
# of interrelations, and we can't easily decompose it further.

# Let me try a different computational approach:
# Process elements from smallest to largest, maintaining a DP state
# that tracks which elements are "eligible" to be placed next.

# An element x is eligible if all proper divisors of x in {1,...,40} have been placed.

# Key insight: since we process elements in some valid topological order,
# the state is an ORDER IDEAL of the poset.

# Let me try to count order ideals and see if the number is manageable.
# I'll enumerate order ideals by adding elements one at a time.

# Start with the empty ideal (just {1} placed implicitly as the first element).
# At each step, we can add any element whose proper divisors are all in the ideal.

# Let me compute the number of order ideals of {2,...,40} under divisibility.

def count_order_ideals(n):
    """Count order ideals of {2,...,n} under divisibility."""
    elements = list(range(2, n+1))
    
    # For each element, find its proper divisors in {2,...,n}
    # (Note: 1 is always "placed", so we only track divisors > 1)
    divisors_in_set = {}
    for x in elements:
        divs = []
        for d in range(2, x):
            if x % d == 0:
                divs.append(d)
        divisors_in_set[x] = divs
    
    # An order ideal is a set I ⊆ {2,...,n} such that if x ∈ I and d|x, d∈{2,...,n}, then d ∈ I.
    # Equivalently, if x ∈ I, then all proper divisors of x in {2,...,n} are in I.
    
    # Generate order ideals using BFS
    # Start with empty set
    ideals = set()
    ideals.add(frozenset())
    
    queue = [frozenset()]
    
    while queue:
        I = queue.pop()
        for x in elements:
            if x not in I:
                if all(d in I for d in divisors_in_set[x]):
                    new_I = I | {x}
                    if new_I not in ideals:
                        ideals.add(new_I)
                        queue.append(new_I)
    
    return len(ideals)

# This is too slow for n=40. Let me try n=20 first.
# Actually, even n=20 might be too slow due to the exponential number of ideals.
# Let me try n=12.

for n in [10, 12, 15]:
    count = count_order_ideals(n)
    print(f"Order ideals of {{2,...,{n}}}: {count}")

