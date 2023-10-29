import asyncio
from time import sleep

async def main():
    # await asyncio.sleep(1)
    return 9

async def main2():
    # asyncio.sleep(1)
    return 9


a=1
a=main()
sleep(2)
print(a)

b=1
b=main2()
sleep(2)
print(b)