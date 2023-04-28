class Smth():
    def __init__(self, text, manager_text) -> None:
        self.text = text
        self.manager_text = manager_text
    
    def manager(func):
        def wraped(*args,**kwargs):
            
            print(args[0].manager_text, '000')
            func(*args,**kwargs)
            print("self.manager_text")
        return wraped
    
    @manager
    def print_smth(self):
        print(self.text)
    
a = Smth('smth', 'manager')
a.print_smth()

        