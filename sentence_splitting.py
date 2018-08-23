import sys
import argparse
import ConfigParser
import re
import codecs
import nltk
import os
nltk.download('punkt')

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

parser=argparse.ArgumentParser()
parser.add_argument('-p', help='Path Parameters')
args=parser.parse_args()
parameters={}
if __name__ == '__main__':
    import sentence_splitting
    parameters = sentence_splitting.ReadParameters(args)     
    sentence_splitting.Main(parameters)

def Main(parameters):
    input_file=parameters['input_file']
    output_file= parameters['output_file']
    classification_token_index=int(parameters['classification_token_index'])
    id_index=int(parameters['id_index'])
    paragraph_index=int(parameters['paragraph_index'])
    if os.path.isdir(input_file):
        sentence_splitting_directory(input_file, output_file, classification_token_index, id_index, paragraph_index)
    else:
        sentence_splitting(input_file, output_file, classification_token_index, id_index, paragraph_index)
    
def ReadParameters(args):
    if(args.p!=None):
        Config = ConfigParser.ConfigParser()
        Config.read(args.p)
        parameters['input_file']=Config.get('MAIN', 'input_file')
        parameters['output_file']=Config.get('MAIN', 'output_file')
        parameters['paragraph_index']=Config.get('MAIN', 'paragraph_index')
        parameters['id_index']=Config.get('MAIN', 'id_index')
        parameters['classification_token_index']=Config.get('MAIN', 'classification_token_index')
    else:
        logging.error("Please send the correct parameters config.properties --help ")
        sys.exit(1)
    return parameters   

def sentence_splitting_directory(input_file, output_file, classification_token_index, id_index, paragraph_index):
    ids_list=[]
    if(os.path.isfile(input_file+"/list_files_standardized_sentences.txt")):
        with open(input_file+"/list_files_standardized_sentences.txt",'r') as ids:
            for line in ids:
                ids_list.append(line.replace("\n",""))
        ids.close()
    if os.path.exists(input_file):
        onlyfiles_toprocess = [os.path.join(input_file, f) for f in os.listdir(input_file) if (os.path.isfile(os.path.join(input_file, f)) & f.endswith('.xml.txt') & (os.path.basename(f) not in ids_list))]
    with open(output_file+"/list_files_standardized_sentences.txt",'a') as list_files_standardized_sentences:    
        for file in onlyfiles_toprocess:    
            output_file_result = output_file + "/" + os.path.basename(file) + "_sentences.txt"
            sentence_splitting(file, output_file_result, classification_token_index, id_index,paragraph_index)
            list_files_standardized_sentences.write(os.path.basename(file)+"\n")
            list_files_standardized_sentences.flush()
    list_files_standardized_sentences.close() 
     
def sentence_splitting(input_file, output_file, classification_token_index, id_index,paragraph_index):
    logging.info("Sentence Spliting for intup file  : " + input_file + ".  output file : "  + output_file)
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    total_articles_errors = 0
    with codecs.open(output_file,'w',encoding='utf8') as sentence_file:
        with codecs.open(input_file,'r',encoding='utf8') as file:
            for line in file:
                try:
                    data = re.split(r'\t+', line) 
                    if(classification_token_index!=-1):
                        classification_token = data[classification_token_index]
                    id = data[id_index]
                    sentence_order = 1
                    parragraph = data[paragraph_index]
                    sentences = tokenizer.tokenize(parragraph)
                    for item in sentences:
                        if(classification_token_index!=-1):
                            sentence_file.write(classification_token + '\t' + id + "_"+str(sentence_order) + '\t' + item.lower() + '\n')
                        else:
                            sentence_file.write(id + "_"+str(sentence_order) + '\t' + item.lower() + '\n')
                        sentence_order=sentence_order + 1
                    sentence_file.flush()
                except Exception as inst:
                    total_articles_errors = total_articles_errors + 1
                    logging.error("The article with id : " + id + " could not be processed. Cause:  " +  str(inst))
                    logging.debug( "Full Line :  " + line)
                    logging.error("The cause probably: contained an invalid character ")
        file.close()       
        logging.info("Total articles with character invalid: "  +  str(total_articles_errors))
        logging.info("Sentence Spliting End")
    sentence_file.close()

