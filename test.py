import re 
import json
     
TRXN_START_PATTERN = re.compile(r'Transaction "(?P<transaction_name>[^"]+)" started')
TRXN_END_PATTERN   = re.compile(r'Transaction "(?P<transaction_name>[^"]+)" ended with a "(?P<transaction_status>[^"]+)" status\s+\(Duration:[^)]+\)')

BACKEND_STEP_START = re.compile(r't=(?P<ts>\d+)ms:\s*(?P<click_step_name>Step.+?Click on[^\[]+)\s+started')
BACKEND_STEP_END = re.compile(r't=(?P<ts>\d+)ms:\s*(?P<click_step_name>Step.+?:\s*Click on[^\[]+?)\s+successfully completed with End Event "Step network completed"')
FRONTEND_STEP_START = re.compile(r't=(?P<ts>\d+)ms:\s*(?P<wait_step_name>Step.+?Wait until[^\[]+)\s+started')
FRONTEND_STEP_END = re.compile(r't=(?P<ts>\d+)ms:\s*(?P<wait_step_name>Step.+?:\s*Wait until[^\[]+?)\s+successfully completed with End Event "Action completed"')

FILE = open ('output_true_client(2).txt', 'r')

class Parser():

    def __init__(self):
        self.transactions = []
        self.logs = []

    def get_next_transaction(self,file):
        i,j=0,0
        for line in file:
            start_token = TRXN_START_PATTERN.search(line) #searching a trxn start
            if start_token:
                break
            i = i+1
        for line in file:
            end_token = TRXN_END_PATTERN.search(line)  # searching a trxn end
            if end_token:
                break
            j = j+1
        endpos = j+1 # position to start next ireration  
        transaction = ("".join(file[i:endpos])) 
        return transaction,endpos

    def get_all_transactions (self): 
        file = FILE.readlines()
        while True:
            trxn,endpos = self.get_next_transaction(file)
            if trxn:
                self.transactions.append(trxn)
                file = file[endpos:]
            else:
                break 
        return self.transactions

    def get_next_log(sefl,transaction): # get the next log in transaction, starts to      search from the the last position (endpos)
        i = 0
        log = {}
        for line in transaction:
            front_start = FRONTEND_STEP_START.search(line)
            back_start = BACKEND_STEP_START.search(line)
            if front_start:
                log['name'] = front_start.group(2)
                log['start time'] = int(front_start.group(1))
                log['step_type'] = 'front_end'
                for line in transaction[i+1:]:
                    front_end = FRONTEND_STEP_END.search(line)
                    if front_end:
                        if front_end.group(2)==front_start.group(2):
                            log['end time']= int(front_end.group(1))
                            log['duration'] = log['end time'] - log['start time']
                            break
                break
            if back_start:
                log['name'] = back_start.group(2)
                log['start time'] = int(back_start.group(1))
                log['step_type'] = 'back_end'
                for line in transaction[i+1:]:
                    back_end = BACKEND_STEP_END.search(line)
                    if back_end:
                        if back_end.group(2)==back_start.group(2):
                            log['end time']= int(back_end.group(1))
                            log['duration'] = log['end time'] - log['start time']
                            break
                break
            i = i + 1
        endpos = i + 1
        return log, endpos

    def get_all_logs(self):
        for transaction in self.get_all_transactions(): 
            text = transaction.split('\n')
            transaction_name = TRXN_START_PATTERN.search(transaction).group(1)
            transaction_status = TRXN_END_PATTERN.search(transaction).group(2)
            while True:
                log, endpos = self.get_next_log(text)
                if len(log) == 0: # if there is no logs left in transaction - break
                    break
                else:
                    if 'duration' in log: 
                        log['transaction name'] = transaction_name
                        log['transaction status'] = transaction_status
                        self.logs.append(log)
                        text = text[endpos:]
                    elif 'duration' not in log: # if log has no end,searching the next one
                        text = text[endpos:] 

    def save_to_json (self):
        with open("data.json",'w') as outfile:
            json.dump(self.logs,outfile)

if __name__ == "__main__":
    test = Parser()
    test.get_all_logs()
    test.save_to_json()
    

    