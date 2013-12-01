# a lot of this is from Tweedr
import crfsuite
import re
from colorama import Fore
import tempfile
from xdoc.formats.tex import serialize_reference
from xdoc.lib.text import utf8str
from unidecode import unidecode
from viz import gloss
# from sklearn import linear_model, naive_bayes, neighbors, svm
# from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

from xdoc.lib.log import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

xml_begin = re.compile('<(\w+)>')
xml_end = re.compile('</(\w+)>')
# tex_command = re.compile(r'\\[a-z]+\{([^\}]+)\}')


def mean(xs):
    return sum(xs) / float(len(xs))


class ItemSequence(crfsuite.ItemSequence):
    def __init__(self, features_iter, check=False):
        '''Create new ItemSequence, typedef std::vector<Item> based on the
        given iterable of iterable of 2-tuples or strings.
        If check=True, any unicode present in the given features_iter
        will be encoded into a bytestring as utf8.'''
        super(ItemSequence, self).__init__()
        self.append_raw(features_iter, check=check)

    def append_raw(self, features_iter, check=False):
        '''
        @features_iter is an iterable of iterables, of tuples or strings.
            type: [[(str, float) | str]], where [] is an iterable
        '''
        for features in features_iter:
            item = crfsuite.Item()
            for feature in features:
                if isinstance(feature, tuple):
                    feature, value = feature
                    if check:
                        feature = utf8str(feature)
                    attribute = crfsuite.Attribute(feature, value)
                else:
                    if check:
                        feature = utf8str(feature)
                    attribute = crfsuite.Attribute(feature)
                item.append(attribute)
            self.append(item)


class CRF(object):
    '''
    Doesn't fit entirely within the classifier paradigm, due to the hierarchy of data:
    Sentences have each token labeled, but each sentence is an individual entity.
    '''
    def __init__(self, algorithm='l2sgd', type_='crf1d'):
        self.trainer = crfsuite.Trainer()
        self.trainer.select(algorithm, type_)
        # default parameters:
        self.trainer.set('c2', '0.1')

    def fit(self, Xys):
        # Xys is an iterable of documents,
        # each document is an iterable of (features, tag) pairs
        # features is an iterable of strings or (string, float) tuples
        # tag is just a string
        for Xy in Xys:
            features, labels = zip(*Xy)
            items = ItemSequence(features, check=True)
            self.trainer.append(items, tuple(labels), 0)

        self.model_filepath = tempfile.NamedTemporaryFile(delete=False).name
        logger.debug('Persisting CRF model to %s', self.model_filepath)
        self.trainer.train(self.model_filepath, -1)
        # persist to file and pull it back out.
        self.tagger = crfsuite.Tagger()
        self.tagger.open(self.model_filepath)

    def get_params(self, help=False):
        params = self.trainer.params()
        return dict((name, self.trainer.help(name) if help else self.trainer.get(name)) for name in params)

    def predict(self, features):
        # only takes one document at a time
        items = ItemSequence(features, check=True)
        # this will just die if self.tagger has not been set
        self.tagger.set(items)
        # could also run self.probability() and self.marginal()
        # convert tuple (output of viterbi()) to list
        return list(self.tagger.viterbi())

    def set_params(self, **params):
        for name, value in params.items():
            self.trainer.set(name, value)

    # def predict_one(self, features_iter):
    #     items = ItemSequence(features_iter, check=True)
    #     self.tagger.set(items)
    #     return list(self.tagger.viterbi())

    # def save(self, model_filepath):
    #     logger.debug('Saving model to %s', model_filepath)
    #     # just die if self.model_filepath doesn't exist
    #     os.rename(self.model_filepath, model_filepath)
    #     self.model_filepath = model_filepath

    # @classmethod
    # def from_file(cls, model_filepath):
    #     '''If we are given a model_filepath that points to an existing file, use it.
    #     otherwise, create a temporary file to store the model because CRFSuite
    #     doesn't seem to allow us to create a tagger directly from a trained
    #     trainer object.'''
    #     # cls = CRF, obviously
    #     crf = cls()
    #     crf.tagger = crfsuite.Tagger()
    #     logger.debug('Loading existing model from %s', model_filepath)
    #     crf.tagger.open(model_filepath)
    #     crf.model_filepath = model_filepath
    #     return crf


def parse_reference_label_sequence(line, missing=None):
    '''
    A reference-label-sequence might look like this:

        <author> A. Cau, R. Kuiper, and W.-P. de Roever. </author> <title> Formalising Dijkstra's development strategy within Stark's formalism. </title> <editor> In C. B. Jones, R. C. Shaw, and T. Denvir, editors, </editor> <booktitle> Proc. 5th. BCS-FACS Refinement Workshop, </booktitle> <date> 1992. </date>

    yields (token, tag) pairs

    In this case, something like [('A.', 'author'), ('Cau,', 'author'), ...]

    TODO: do something more intelligent with the
    '''
    tag = missing
    tokens = line.split()
    for token in tokens:
        tag_begin = xml_begin.match(token)
        tag_end = xml_end.match(token)

        if tag_begin:
            tag = tag_begin.group(1)
        elif tag_end:
            assert tag_end.group(1) == tag, 'Bad XML nesting: %s != %s' % (tag_end.group(1), tag)
            tag = missing
        else:
            yield (token, tag)


def token_features(token):
    # takes a single string token and
    # yields strings representing features of this token
    yield token
    lower = token.lower()
    yield lower
    yield lower.strip('\'",.?;:')
    yield ('length', float(len(token)))
    yield ('digits', float(sum(1 for char in token if char.isdigit())))


def open_parscit_corpus():
    filepath = '/Users/chbrown/corpora-public/parsCit/tagged_references.txt'
    # the tagged_references has lines like this:
    # raw = "<author> A. Cau, R. Kuiper, and W.-P. de Roever. </author> <title> Formalising Dijkstra's development strategy within Stark's formalism. </title> <editor> In C. B. Jones, R. C. Shaw, and T. Denvir, editors, </editor> <booktitle> Proc. 5th. BCS-FACS Refinement Workshop, </booktitle> <date> 1992. </date>"
    for line in open(filepath):
        yield line


def open_cora_corpus():
    filepath = '/Users/chbrown/corpora-public/cora/classify/papers'
    # e.g., 272	http:##www.cs.rpi.edu#tr#93-21.ps	[39] <author> C. V. Stewart. MINPRAN: </author> <title> A new robust estimator for computer vision. </title> <journal> IEEE PAMI, </journal> <volume> 17(10):925 938, </volume> <month> Oct. </month> <year> 1995. </year>
    for line in open(filepath):
        cora_id, url, full = line.split('\t')
        citation = full.strip()
        if citation:
            # remove the '[inline] ' bit from lines like: '[inline] good stuff ...'
            #citation = re.sub(r'^\[.+?\]\s+', '', full)
            # skip to the first tag, marked by a '<',
            # first_lt_index = full.index('<')
            # last_gt_index = full.rindex('>')
            # citation = full[first_lt_index:last_gt_index + 1]
            yield citation


def get_corpus(source):
    '''
    source is an iterator over lines formatted like '<author> J. J. Abe </author> <title> He ... </title> ...'

    yields (features, label) pairs
    '''
    for line in source:
        token_label_pairs = parse_reference_label_sequence(line, missing='none')
        # tokens, labels = zip(*token_label_pairs)

        # print gloss.gloss(document, prefixes=('', Fore.RED), postfixes=(Fore.RESET, Fore.RESET))
        features_label_pairs = ((list(token_features(token)), label) for token, label in token_label_pairs)
        yield features_label_pairs


def train_crf():
    '''
    returns CRF object
    '''
    corpus = get_corpus(open_cora_corpus())

    crf = CRF()
    crf.fit(corpus)
    print 'Done fitting CRF'

    return crf


def evaluate():
    from sklearn import cross_validation, metrics

    corpus = get_corpus(open_cora_corpus())
    N = len(corpus)
    accuracies = []

    for k, (train_indices, test_indices) in enumerate(cross_validation.KFold(N, n_folds=5, shuffle=True)):
        logger.debug('Iteration #%d', k)

        train = map(corpus.__getitem__, train_indices)
        test = map(corpus.__getitem__, test_indices)
        logger.info('Training on %d, testing on %d', len(train), len(test))

        crf = CRF()
        crf.fit(train)
        logger.debug('Finished fitting CRF')

        def align_labels(documents):
            for document in documents:
                features, labels_gold = zip(*document)
                labels_predicted = crf.predict(features)

                for label_gold, label_predicted in zip(labels_gold, labels_predicted):
                    yield label_gold, label_predicted

        aligned_labels = align_labels(test)
        labels_gold, labels_predicted = zip(*aligned_labels)

        logger.debug('%d gold == %d predicted', len(labels_gold), len(labels_predicted))
        accuracy = metrics.accuracy_score(labels_gold, labels_predicted)
        accuracies.append(accuracy)
        logger.debug('', k)
        logger.info('Iteration #%d, accuracy: %0.5f', k, accuracy)

    logger.info('Average accuracy: %0.5f', mean(accuracies))
