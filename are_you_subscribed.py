import requests, time

def are_you_subscribed():
    #import macID.txt and turn into an obj
    #macID_txt = '/root/macID.txt'
    macID_txt = '/Users/oli/Desktop/macID.txt'
    macIDlist = open(macID_txt,'r').read().split('\n')
    macID = macIDlist[0]
    #import unsub list and turn into a list
    #unsub_txt = '/root/wthr-pstr/unsubscribed.txt'
    unsub_txt = '/Users/oli/Desktop/unsubscribed.txt'
    unsub = open(unsub_txt,'r').read().split('\n')
    if macID in unsub:
        return 'unsubscribed'
    else:
        return 'subscribed'
