import time
import os



class CostTime:

    name: str

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.perf_counter()
        count = end_time - self.start_time
        Debug.log('Debug', f'{self.name} {count // 60:.0f} min {count - count // 60 * 60:.3f} s')


class Debug:

    @staticmethod
    def log(tag: str, mes: str, type: int = 0, end = '\n') -> None:
        output = "[" + time.strftime('%H:%M:%S', time.localtime(time.time())) + "] (" + tag + ") " + mes
        print(output, end=end)
        if type == 0:
            os.makedirs('runs', exist_ok=True)
            with open(f'runs/log.txt', 'a') as f:
                f.write(output + "\n")
    
    @staticmethod
    def arrayToStr(mes) -> None:
        output = "[ "
        for e in mes:
            output += "{:3}".format(e) + ", "
        return output + "]"