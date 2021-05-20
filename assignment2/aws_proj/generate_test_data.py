rmit_id = "s3805449"
name = "piyush"
users = []
with open("samples/users_copy.json", "w") as f:
    for i in range(0, 10):
        d = {
            "email": "{}{}@student.rmit.edu.com".format(rmit_id, i),
            "username": "{}{}".format(name, i),
            "password": "12345678{}".format(i)
        }
        users.append(d)
    f.write(str(users).replace("'", '"'))
