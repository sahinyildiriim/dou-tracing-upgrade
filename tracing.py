import time
import functools
from typing import Callable, Any

class Tracer:
    def __init__(self):
        self.traces = []
    
    def trace(self, func: Callable) -> Callable:
        """Decorator to trace function calls"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time
                
                self.traces.append({
                    'function': func_name,
                    'args': args,
                    'kwargs': kwargs,
                    'duration': duration,
                    'status': 'success',
                    'result': result
                })
                
                return result
            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time
                
                self.traces.append({
                    'function': func_name,
                    'args': args,
                    'kwargs': kwargs,
                    'duration': duration,
                    'status': 'error',
                    'error': str(e)
                })
                raise
        
        return wrapper
    
    def report(self):
        """Print a report of all traced function calls"""
        if not self.traces:
            print("No traces recorded.")
            return
        
        print("\n" + "="*60)
        print("TRACING REPORT")
        print("="*60)
        
        for i, trace in enumerate(self.traces, 1):
            print(f"\n[{i}] Function: {trace['function']}")
            print(f"    Duration: {trace['duration']:.4f} seconds")
            print(f"    Status: {trace['status']}")
            
            if trace['args']:
                print(f"    Args: {trace['args']}")
            if trace['kwargs']:
                print(f"    Kwargs: {trace['kwargs']}")
            
            if trace['status'] == 'error':
                print(f"    Error: {trace['error']}")
            elif 'result' in trace:
                print(f"    Result: {trace['result']}")
        
        print("\n" + "="*60)
        print(f"Total traces: {len(self.traces)}")
        total_duration = sum(t['duration'] for t in self.traces)
        print(f"Total duration: {total_duration:.4f} seconds")
        print("="*60 + "\n")

