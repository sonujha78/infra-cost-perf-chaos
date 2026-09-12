# Deliberately inefficient prime-checking — O(n) trial division per number,
# no early exits beyond sqrt, checking even numbers unnecessarily
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, n):   # BUG: should stop at sqrt(n), not n
        if n % i == 0:
            return False
    return True

count = 0
for num in range(2, 200000):
    if is_prime(num):
        count += 1
print(f"Found {count} primes")
