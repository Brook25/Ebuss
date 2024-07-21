from better_profanity import profanity

def check_vulgarity(word):
    if profanity.contains_profane(word):
        raise ValdiationError('your name contains a prohibited word.')
