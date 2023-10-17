import asyncio
from time import sleep

async def func_1():
    sleep(3)
    print("func 1")

def func_2():
    sleep(2)
    print("func 2")

def func_3():
    print("func 3")

def func_4():
    print("func 4")    

async def big_function():
    await func_1()  # Assuming command_1 is an async function
    func_2()  # Assuming command_2 is a synchronous function

async def main():
    task1 = asyncio.create_task(big_function())
    func_3()  # Assuming command_3 is a synchronous function
    await task1  # Optionally wait for function_1 to complete
    func_4()

# Run the main function to kick off asynchronous execution
if __name__ == '__main__':
    asyncio.run(main())
