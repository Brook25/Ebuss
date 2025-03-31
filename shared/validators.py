from better_profanity import profanity

def check_vulgarity(word):
    if profanity.contains_profanity(word):
        raise ValdiationError('your name contains a prohibited word.')
