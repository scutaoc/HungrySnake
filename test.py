if __name__ == '__main__':
    # a = 1
    action(a)
    b = a + 1
    print(a)
    import json

    filename = 'username.json'
    try: # 如果以前存储了用户名，就加载它
        with open(filename, 'r') as f:
            username = json.load(f)
    except FileNotFoundError: # 否则，就提示用户输入用户名并存储它
        username = input("What is your name?")
        with open(filename, 'w') as f:
            json.dump(username, f)
            print("We'll remember you when you come back, " + username + "!")
    else:
        print("Welcome back, " + username + "!")




