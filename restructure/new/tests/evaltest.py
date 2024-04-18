class holder():
    def test_exec(self):
        print("ran")

def test(holder):
    localVar = "holder.test_exec()"
    exec(localVar)

test(holder())