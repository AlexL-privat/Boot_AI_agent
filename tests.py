from functions.run_python_file import run_python_file

def run_tests():
    test_cases = [
        ("calculator", "main.py",[]),
        ("calculator", "main.py", ["3 + 5"]),
        ("calculator", "tests.py",[]),
        ("calculator", "../main.py",[]),
        ("calculator", "nonexistent.py",[]),
        ("calculator", "lorem.txt",[])
    ]

    for working_directory, file_path, args in test_cases:
            result = run_python_file(working_directory, file_path, args)
            print(f"Result for {file_path}:")
            if result.startswith("Error:"):
                print(f"    {result}")
            else:
                for line in result.splitlines():
                    print(f" {line}")


if __name__ == "__main__":
    run_tests()