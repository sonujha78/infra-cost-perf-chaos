import math

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):   # FIX: only check up to sqrt(n)
        if n % i == 0:
            return False
    return True

count = 0
for num in range(2, 200000):
    if is_prime(num):
        count += 1
print(f"Found {count} primes")
