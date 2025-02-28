import random
import time

class MathGame:
    def __init__(self):
        self.operations = ['+', '-']
        self.current_level = 1
        self.max_number = 10  # Start with single digit
        self.time_limit = 10  # seconds
        
    def generate_equation(self):
        """Generate a random equation with answer"""
        operation = random.choice(self.operations)
        
        # Adjust difficulty based on level
        max_num = min(self.max_number + self.current_level, 100)
        
        if operation == '+':
            num1 = random.randint(1, max_num)
            num2 = random.randint(1, max_num)
            result = num1 + num2
        else:  # Subtraction
            num1 = random.randint(1, max_num)
            num2 = random.randint(1, num1)  # Ensure positive result
            result = num1 - num2
        
        # Randomly decide if we should show correct or incorrect equation
        is_correct = random.choice([True, False])
        
        if not is_correct:
            # Make the result incorrect by adding or subtracting a small number
            offset = random.randint(1, 5)
            result = result + offset if random.choice([True, False]) else result - offset
        
        equation = f"{num1} {operation} {num2} = {result}"
        
        return {
            "equation": equation,
            "is_correct": is_correct,
            "time_limit": self.get_time_limit()
        }
    
    def get_time_limit(self):
        """Get time limit for current level"""
        # Decrease time limit as level increases, but not below 2 seconds
        return max(self.time_limit - (self.current_level * 0.5), 2)
    
    def increase_level(self):
        """Increase game level"""
        self.current_level += 1
        
        # Every 5 levels, increase max number
        if self.current_level % 5 == 0:
            self.max_number += 10
