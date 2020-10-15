import asyncio
import Async_hCaptcha
import sys

if __name__ == "__main__":
    #asyncio.run(Async_hCaptcha.Hcaptcha_Handler('caspers.app','eaaffc67-ea9f-4844-9740-9eefd238c7dc'))
    asyncio.run(Async_hCaptcha.Hcaptcha_Handler(str(sys.argv[1]),str(sys.argv[2])))