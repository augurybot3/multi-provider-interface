import random

class TongueTwisters:
    def __init__(self):
        self.voice = ""
        self.identity_statement = ""
        self.betty_botter = "Betty Botter bought some butter but she said the butter\'s bitter. If I put it in my batter, it will make my batter bitter but a bit of better butter will make my batter better. So \'twas better Betty Botter bought a bit of better butter"
        self.peter_piper = "Peter Piper picked a peck of pickled peppers. A peck of pickled peppers Peter Piper picked. If Peter Piper picked a peck of pickled peppers, Where\'s the peck of pickled peppers Peter Piper picked?"
        self.peter_pipers_plan = """Peter Piper picked a peck of pickled peppers. A peck of pickled peppers Peter Piper picked. If Peter Piper picked a peck of pickled peppers, Where's the peck of pickled peppers Peter Piper picked? Pregnant Peggy pondered,  "perhaps precious Peter played pecked picked pickles improperly? Perhaps Poor Peter picked his pickled peppers on purpose!" Profusely, Pregnant Peggy proudly pronounced, "Pious Peter Piper planned as was probably prepared prior to picking! Where's the peck of pickled peppers Peter!? Peter plainly plundered purple packed pecks of pickled peppers prior to even politely pretending to pick a pickled pair! Pious Peter Piper picking pecked pickled peppers, please!" Passionate pregnant Peggy pointed out  Peter Piper's plan."""
        self.woodchuck = "How much wood would a woodchuck chuck if a woodchuck could chuck wood? He would chuck, he would, as much as he could, and chuck as much wood As a woodchuck would if a woodchuck could chuck wood"
        self.classic_twists = [self.betty_botter, self.peter_piper, self.peter_pipers_plan, self.woodchuck]
        self.triple_twists = self.triple_twist()
        self.quick_twists = ["She sells seashells by the seashore.","How can a clam cram in a clean cream can?","I scream, you scream, we all scream for ice cream.","I saw Susie sitting in a shoeshine shop.","Susie works in a shoeshine shop. Where she shines she sits, and where she sits she shines.","Fuzzy Wuzzy was a bear. Fuzzy Wuzzy had no hair. Fuzzy Wuzzy wasn\'t fuzzy, was he?","Can you can a can as a canner can can a can?","I have got a date at a quarter to eight; I'll see you at the gate, so don\'t be late.","You know New York, you need New York, you know you need unique New York.","I saw a kitten eating chicken in the kitchen.","If a dog chews shoes, whose shoes does he choose?","I thought I thought of thinking of thanking you.","I wish to wash my Irish wristwatch.","Near an ear, a nearer ear, a nearly eerie ear.","Eddie edited it.","Willie\'s really weary.","A big black bear sat on a big black rug.","Tom threw Tim three thumbtacks.","He threw three free throws.","Nine nice night nurses nursing nicely.","So, this is the sushi chef.","Four fine fresh fish for you.","Wayne went to wales to watch walruses.","We surely shall see the sun shine soon.","Which wristwatches are Swiss wristwatches?","Fred fed Ted bread, and Ted fed Fred bread.","I slit the sheet, the sheet I slit, and on the slitted sheet I sit.","A skunk sat on a stump and thunk the stump stunk, but the stump thunk the skunk stunk.","Lesser leather never weathered wetter weather better.",
            "Of all the vids I\'ve ever viewed, I\'ve never viewed a vid as valued as Alex\'s engVid vid"]
        self.twists = {"betty_botter":self.betty_botter,"peter_piper":self.peter_piper,"woodchuck":self.woodchuck,"triple_twisters":self.triple_twists,"quick_twisters":self.quick_twists}
        self.twist = self.get_random_twist()
        
    def identify(self, voice):
        self.voice = voice
        return f"This is {voice} speaking. You're listening to the a.i. generated voice of {voice}. I am {voice}."

    def get_random_index(self, items):
        if not items:
            return None  # or raise an exception
        random_index = random.randint(0, len(items) - 1)
        return random_index

    def get_random_quick_twist(self):
        random_index = self.get_random_index(self.quick_twists)
        return self.quick_twists[random_index] if random_index is not None else None

    def get_random_triple_twist(self):
        random_index = self.get_random_index(self.triple_twists)
        return self.triple_twists[random_index] if random_index is not None else None

    def get_random_classic(self):
        random_index = self.get_random_index(self.classic_twists)
        return self.classic_twists[random_index] if random_index is not None else None
    
    def get_random_twist(self):
        twist_type = random.choice(list(self.twists.keys()))
        if twist_type in ["betty_botter", "peter_piper", "woodchuck"]:
            return self.get_random_classic()
        elif twist_type == "triple_twisters":
            return self.get_random_triple_twist()
        elif twist_type == "quick_twisters":
            return self.get_random_quick_twist()
        return None  # fallback, should not hit this
        
    def triple_twist(self):
        triple_twisters = [
            "Six sticky skeletons ",
            "Which witch is which? ",
            "Snap crackle pop ",
            "Flash message ",
            "Red Buick, blue Buick ",
            "Red lorry, yellow lorry ",
            "Thin sticks, thick bricks ",
            "Stupid superstition ",
            "Eleven benevolent elephants ",
            "Two tried and true tridents ",
            "Rolling red wagons ",
            "Black back bat ",
            "She sees cheese ",
            "Truly rural ",
            "Good blood, bad blood ",
            "Pre-shrunk silk shirts ",
            "Ed had edited it ",
            "Simple Simpsons Satire  "]
        
        triple_twists = []
        for twister in triple_twisters:
            triplicated_twist = f'{twister} {twister} {twister}'
            triple_twists.append(triplicated_twist)
            
        return triple_twists
    
class FlattenData:
    def __init__(self):
        self.twists = TongueTwisters()
        self.classic_twists = self.twists.classic_twists
        self.quick_twists =   self.twists.quick_twists
        self.triple_twists =  self.twists.triple_twists
    
    def flatten_twists(self):
        twists = []
        twists.extend(self.classic_twists)
        twists.extend(self.quick_twists)
        twists.extend(self.triple_twists)
        return twists