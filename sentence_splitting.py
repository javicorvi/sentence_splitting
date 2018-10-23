import sys
import argparse
import ConfigParser
import re
import codecs
import nltk 
import os


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
    nltk.download('punkt')
    is_training = parameters['is_training']
    input_file=parameters['input_file']
    output_file= parameters['output_file']
    classification_token_index=int(parameters['classification_token_index'])
    id_index=int(parameters['id_index'])
    section_index=int(parameters['section_index'])
    sourceId_index=int(parameters['sourceId_index'])
    paragraph_index=int(parameters['paragraph_index'])
    if is_training == 'false' and os.path.isdir(input_file):
        #if is not a training is classification and a directory has to be processed
        sentence_splitting_directory(is_training, input_file, output_file, classification_token_index, id_index, sourceId_index, section_index, paragraph_index)
    elif is_training == 'true' and os.path.isfile(input_file):
        # Is training and the input has to be a unique file
        sentence_splitting(is_training, input_file, output_file, classification_token_index, id_index, sourceId_index, section_index, paragraph_index)
    
def ReadParameters(args):
    if(args.p!=None):
        Config = ConfigParser.ConfigParser()
        Config.read(args.p)
        parameters['is_training']=Config.get('MAIN', 'is_training')
        parameters['input_file']=Config.get('MAIN', 'input_file')
        parameters['output_file']=Config.get('MAIN', 'output_file')
        parameters['paragraph_index']=Config.get('MAIN', 'paragraph_index')
        parameters['id_index']=Config.get('MAIN', 'id_index')
        parameters['section_index']=Config.get('MAIN', 'section_index')
        parameters['sourceId_index']=Config.get('MAIN', 'sourceId_index')
        parameters['classification_token_index']=Config.get('MAIN', 'classification_token_index')
    else:
        logging.error("Please send the correct parameters config.properties --help ")
        sys.exit(1)
    return parameters   

def sentence_splitting_directory(is_training, input_file, output_file, classification_token_index, id_index, sourceId_index, section_index, paragraph_index):
    logging.info("Sentence Spliting for directory  : " + input_file + ".  output file : "  + output_file + " -- mode training " + str(is_training))
    if not os.path.exists(output_file):
        os.makedirs(output_file)
    ids_list=[]
    if(os.path.isfile(output_file+"/list_files_processed.dat")):
        with open(output_file+"/list_files_processed.dat",'r') as ids:
            for line in ids:
                ids_list.append(line.replace("\n",""))
        ids.close()
    if os.path.exists(input_file):
        onlyfiles_toprocess = [os.path.join(input_file, f) for f in os.listdir(input_file) if (os.path.isfile(os.path.join(input_file, f)) & f.endswith('.xml.txt') & (os.path.basename(f) not in ids_list))]
    with open(output_file+"/list_files_processed.dat",'a') as list_files_standardized_sentences:    
        for file in onlyfiles_toprocess:    
            output_file_result = output_file + "/" + os.path.basename(file)
            sentence_splitting(is_training, file, output_file_result, classification_token_index, id_index, sourceId_index, section_index, paragraph_index)
            list_files_standardized_sentences.write(os.path.basename(file)+"\n")
            list_files_standardized_sentences.flush()
    list_files_standardized_sentences.close() 
    logging.info("End Sentence Spliting") 
def sentence_splitting(is_training, input_file, output_file, classification_token_index, id_index, sourceId_index, section_index, paragraph_index):
    logging.info("Sentence Spliting for intup file  : " + input_file + ".  output file : "  + output_file + " mode training " + str(is_training))
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    total_articles_errors = 0
    with codecs.open(output_file,'w',encoding='utf8') as sentence_file:
        with codecs.open(input_file,'r',encoding='utf8') as file:
            for line in file:
                try:
                    data = re.split(r'\t+', line)
                    if(len(data)>=4): 
                        if(classification_token_index!=-1):
                            classification_token = data[classification_token_index]
                        id = data[id_index]
                        #print id
                        sentence_order = 1
                        parragraph = data[paragraph_index]
                        sentences = tokenizer.tokenize(parragraph)
                        for item in sentences:
                            if is_training == 'false' :
                                sourceId = data[sourceId_index]
                                section = data[section_index]
                                sentence_file.write(id + "_"+str(sentence_order)  + '\t' + sourceId  + '\t' + section + '\t' + item +  '\n') 
                            elif is_training == 'true' :
                                #The training add the classification token
                                sentence_file.write(classification_token + '\t' + id + "_"+str(sentence_order)+ '\t' + item +  '\n') 
                            sentence_order=sentence_order + 1
                        sentence_file.flush()
                    else:
                        logging.error("The article with id : " + id + " could not be processed. Five columns has to be present separated in tabs  " )
                        logging.debug( "Full Line :  " + line)
                        logging.debug( "File :  " + input_file)
                except Exception as inst:
                    total_articles_errors = total_articles_errors + 1
                    logging.error("The article with id : " + id + " could not be processed. Cause:  " +  str(inst))
                    logging.debug( "Full Line :  " + line)
                    logging.debug( "File :  " + input_file)
                    logging.error("The cause probably: contained an invalid character ")
        file.close()       
        logging.info("Total articles with character invalid: "  +  str(total_articles_errors))
        logging.info("Sentence Spliting End")
    sentence_file.close()

