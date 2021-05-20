rmit_id = "s123456"
name = "Test User"
users = []
with open("samples/users_copy.json", "w") as f:
    for i in range(0, 10):
        d = {
            "email": "{}{}@student.com".format(rmit_id, i),
            "username": "{}{}".format(name, i),
            "password": "12345678{}".format(i)
        }
        users.append(d)
    f.write(str(users).replace("'", '"'))
