import { describe, it, expect } from 'vitest';
import { detectProgrammingLanguage, calculateCodeStats, generateAutoTitle } from './languageDetection';

describe('Language Detection Utility', () => {
  describe('detectProgrammingLanguage', () => {
    it('should detect Python code', () => {
      const pythonCode = `
def hello_world():
    print("Hello, World!")
    for i in range(5):
        print(f"Iteration {i}")

if __name__ == "__main__":
    hello_world()
      `;
      expect(detectProgrammingLanguage(pythonCode)).toBe('python');
    });

    it('should detect JavaScript code', () => {
      const jsCode = `
function helloWorld() {
  console.log("Hello, World!");
  const numbers = [1, 2, 3, 4, 5];
  numbers.forEach(num => console.log(num));
}

const arrowFunction = () => {
  return "This is an arrow function";
};
      `;
      expect(detectProgrammingLanguage(jsCode)).toBe('javascript');
    });

    it('should detect TypeScript code', () => {
      const tsCode = `
interface User {
  id: number;
  name: string;
  email?: string;
}

function greetUser(user: User): string {
  return \`Hello, \${user.name}!\`;
}

const user: User = {
  id: 1,
  name: "John Doe"
};
      `;
      expect(detectProgrammingLanguage(tsCode)).toBe('typescript');
    });

    it('should detect Java code', () => {
      const javaCode = `
public class HelloWorld {
    private String message;

    public HelloWorld(String message) {
        this.message = message;
    }

    public void printMessage() {
        System.out.println(message);
    }

    public static void main(String[] args) {
        HelloWorld hw = new HelloWorld("Hello, World!");
        hw.printMessage();
    }
}
      `;
      expect(detectProgrammingLanguage(javaCode)).toBe('java');
    });

    it('should detect C# code', () => {
      const csharpCode = `
using System;

public class Program
{
    public static void Main()
    {
        Console.WriteLine("Hello, World!");
        var numbers = new List<int> { 1, 2, 3, 4, 5 };

        foreach (var num in numbers)
        {
            Console.WriteLine(num);
        }
    }
}
      `;
      expect(detectProgrammingLanguage(csharpCode)).toBe('c#');
    });

    it('should detect PHP code', () => {
      const phpCode = `
<?php
function helloWorld() {
    echo "Hello, World!";
    $numbers = [1, 2, 3, 4, 5];

    foreach ($numbers as $number) {
        echo $number;
    }
}

$user = new stdClass();
$user->name = "John Doe";
echo $user->name;
?>
      `;
      expect(detectProgrammingLanguage(phpCode)).toBe('php');
    });

    it('should detect Go code', () => {
      const goCode = `
package main

import "fmt"

func helloWorld() {
    fmt.Println("Hello, World!")
    numbers := []int{1, 2, 3, 4, 5}

    for _, num := range numbers {
        fmt.Println(num)
    }
}

func main() {
    helloWorld()
}
      `;
      expect(detectProgrammingLanguage(goCode)).toBe('go');
    });

    it('should detect Rust code', () => {
      const rustCode = `
fn main() {
    println!("Hello, World!");
    let numbers = vec![1, 2, 3, 4, 5];

    for num in &numbers {
        println!("{}", num);
    }
}

fn greet_user(name: &str) -> String {
    format!("Hello, {}!", name)
}
      `;
      expect(detectProgrammingLanguage(rustCode)).toBe('rust');
    });

    it('should detect Ruby code', () => {
      const rubyCode = `
def hello_world
  puts "Hello, World!"
  numbers = [1, 2, 3, 4, 5]

  numbers.each do |num|
    puts num
  end
end

class User
  attr_accessor :name, :email

  def initialize(name, email)
    @name = name
    @email = email
  end
end
      `;
      expect(detectProgrammingLanguage(rubyCode)).toBe('ruby');
    });

    it('should detect HTML code', () => {
      const htmlCode = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Hello World</title>
</head>
<body>
    <h1>Hello, World!</h1>
    <div class="container">
        <p>This is a paragraph.</p>
        <button onclick="alert('Click!')">Click me</button>
    </div>
</body>
</html>
      `;
      expect(detectProgrammingLanguage(htmlCode)).toBe('html');
    });

    it('should detect CSS code', () => {
      const cssCode = `
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.button {
    background-color: #007bff;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.button:hover {
    background-color: #0056b3;
}
      `;
      expect(detectProgrammingLanguage(cssCode)).toBe('css');
    });

    it('should detect SQL code', () => {
      const sqlCode = `
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT u.*, p.title
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
WHERE u.created_at >= '2023-01-01'
ORDER BY u.created_at DESC;
      `;
      expect(detectProgrammingLanguage(sqlCode)).toBe('sql');
    });

    it('should return "text" for unknown language', () => {
      const unknownCode = `
This is just plain text
with some random content
and no programming patterns.
      `;
      expect(detectProgrammingLanguage(unknownCode)).toBe('text');
    });

    it('should handle empty string', () => {
      expect(detectProgrammingLanguage('')).toBe('text');
    });

    it('should handle null/undefined input', () => {
      expect(detectProgrammingLanguage(null as any)).toBe('text');
      expect(detectProgrammingLanguage(undefined as any)).toBe('text');
    });
  });

  describe('calculateCodeStats', () => {
    it('should calculate lines and characters correctly', () => {
      const code = `line 1
line 2
line 3`;

      const stats = calculateCodeStats(code);

      expect(stats.linesCount).toBe(3);
      expect(stats.charactersCount).toBe(code.length);
    });

    it('should handle empty code', () => {
      const stats = calculateCodeStats('');

      expect(stats.linesCount).toBe(0);
      expect(stats.charactersCount).toBe(0);
    });

    it('should handle code with only whitespace', () => {
      const code = '   \n  \n   ';
      const stats = calculateCodeStats(code);

      expect(stats.linesCount).toBe(3);
      expect(stats.charactersCount).toBe(code.length);
    });

    it('should handle single line without newline', () => {
      const code = 'single line of code';
      const stats = calculateCodeStats(code);

      expect(stats.linesCount).toBe(1);
      expect(stats.charactersCount).toBe(code.length);
    });
  });

  describe('generateAutoTitle', () => {
    it('should generate title with language and timestamp', () => {
      const language = 'javascript';
      const date = new Date('2023-12-08T10:30:00Z');

      const title = generateAutoTitle(language, date);

      expect(title).toMatch(/^JavaScript Code - \d{4}-\d{2}-\d{2} \d{2}:\d{2}$/);
    });

    it('should handle unknown language', () => {
      const language = 'unknown';
      const date = new Date('2023-12-08T10:30:00Z');

      const title = generateAutoTitle(language, date);

      expect(title).toMatch(/^Code - \d{4}-\d{2}-\d{2} \d{2}:\d{2}$/);
    });

    it('should use current date when not provided', () => {
      const language = 'python';

      const title = generateAutoTitle(language);

      expect(title).toMatch(/^Python Code - \d{4}-\d{2}-\d{2} \d{2}:\d{2}$/);
    });

    it('should capitalize first letter of language', () => {
      const language = 'typescript';

      const title = generateAutoTitle(language);

      expect(title).toMatch(/^Typescript Code/);
    });
  });
});