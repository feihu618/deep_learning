# -*- coding: utf-8 -*-
import sys
import six
import re
import pdfminer.settings
from pdfminer.image import ImageWriter
import pdfminer.layout
import pdfminer.high_level
from gensim import utils
import os
from os.path import join, getsize

pdfminer.settings.STRICT = False

fp = '/home/weiwu/share/deep_learning/data/docs/raw/20170122-长江证券-长江证券金融工程：基于网络的动量选股策略.pdf'
fp = '/home/weiwu/share/deep_learning/docs/word_embedding/Learning Composition Models for Phrase Embedding.pdf'
fp = '/home/weiwu/share/deep_learning/docs/word_embedding/1803.06581.pdf'
fout = './data/research.txt'
f_parsed = './data/research_converted.txt'
max_page_num = '90'


def extract_text(
        files=[],
        outfile='-',
        _py2_no_more_posargs=None,  # Bloody Python2 needs a shim
        no_laparams=False,
        all_texts=None,
        detect_vertical=None,  # LAParams
        word_margin=None,
        char_margin=None,
        line_margin=None,
        boxes_flow=None,  # LAParams
        output_type='text',
        codec='utf-8',
        strip_control=False,
        maxpages=0,
        page_numbers=None,
        password="",
        scale=1.0,
        rotation=0,
        layoutmode='normal',
        output_dir=None,
        debug=False,
        disable_caching=False,
        **other):
    if _py2_no_more_posargs is not None:
        raise ValueError("Too many positional arguments passed.")
    if not files:
        raise ValueError("Must provide files to work upon!")

    # If any LAParams group arguments were passed, create an LAParams object and
    # populate with given args. Otherwise, set it to None.
    if not no_laparams:
        laparams = pdfminer.layout.LAParams()
        for param in ("all_texts", "detect_vertical", "word_margin",
                      "char_margin", "line_margin", "boxes_flow"):
            paramv = locals().get(param, None)
            if paramv is not None:
                setattr(laparams, param, paramv)
    else:
        laparams = None

    imagewriter = None
    if output_dir:
        imagewriter = ImageWriter(output_dir)

    if output_type == "text" and outfile != "-":
        for override, alttype in ((".htm", "html"), (".html", "html"),
                                  (".xml", "xml"), (".tag", "tag")):
            if outfile.endswith(override):
                output_type = alttype

    if outfile == "-":
        outfp = sys.stdout
        if outfp.encoding is not None:
            codec = 'utf-8'
    else:
        outfp = open(outfile, "wb")

    for fname in files:
        with open(fname, "rb") as fp:
            pdfminer.high_level.extract_text_to_fp(fp, **locals())
    return outfp


def convert_pdf2txt(args=None):
    import argparse
    P = argparse.ArgumentParser(description=__doc__)
    P.add_argument(
        "files", type=str, default=None, nargs="+", help="Files to process.")
    P.add_argument(
        "-d",
        "--debug",
        default=False,
        action="store_true",
        help="Debug output.")
    P.add_argument(
        "-p",
        "--pagenos",
        type=str,
        help=
        "Comma-separated list of page numbers to parse. Included for legacy applications, use -P/--page-numbers for more idiomatic argument entry."
    )
    P.add_argument(
        "--page-numbers",
        type=int,
        default=None,
        nargs="+",
        help=
        "Alternative to --pagenos with space-separated numbers; supercedes --pagenos where it is used."
    )
    P.add_argument(
        "-m", "--maxpages", type=int, default=0, help="Maximum pages to parse")
    P.add_argument(
        "-P",
        "--password",
        type=str,
        default="",
        help="Decryption password for PDF")
    P.add_argument(
        "-o",
        "--outfile",
        type=str,
        default="-",
        help="Output file (default/'-' is stdout)")
    P.add_argument(
        "-t",
        "--output_type",
        type=str,
        default="text",
        help="Output type: text|html|xml|tag (default is text)")
    P.add_argument(
        "-c", "--codec", type=str, default="utf-8", help="Text encoding")
    P.add_argument("-s", "--scale", type=float, default=1.0, help="Scale")
    P.add_argument(
        "-A",
        "--all-texts",
        default=None,
        action="store_true",
        help="LAParams all texts")
    P.add_argument(
        "-V",
        "--detect-vertical",
        default=None,
        action="store_true",
        help="LAParams detect vertical")
    P.add_argument(
        "-W",
        "--word-margin",
        type=float,
        default=None,
        help="LAParams word margin")
    P.add_argument(
        "-M",
        "--char-margin",
        type=float,
        default=None,
        help="LAParams char margin")
    P.add_argument(
        "-L",
        "--line-margin",
        type=float,
        default=None,
        help="LAParams line margin")
    P.add_argument(
        "-F",
        "--boxes-flow",
        type=float,
        default=None,
        help="LAParams boxes flow")
    P.add_argument(
        "-Y",
        "--layoutmode",
        default="normal",
        type=str,
        help="HTML Layout Mode")
    P.add_argument(
        "-n",
        "--no-laparams",
        default=False,
        action="store_true",
        help="Pass None as LAParams")
    P.add_argument("-R", "--rotation", default=0, type=int, help="Rotation")
    P.add_argument(
        "-O", "--output-dir", default=None, help="Output directory for images")
    P.add_argument(
        "-C",
        "--disable-caching",
        default=False,
        action="store_true",
        help="Disable caching")
    P.add_argument(
        "-S",
        "--strip-control",
        default=False,
        action="store_true",
        help="Strip control in XML mode")
    # A = P.parse_args(args=[fp, '--outfile', fout])
    A = P.parse_args(args=args)

    if A.page_numbers:
        A.page_numbers = set([x - 1 for x in A.page_numbers])
    if A.pagenos:
        A.page_numbers = set([int(x) - 1 for x in A.pagenos.split(",")])

    imagewriter = None
    if A.output_dir:
        imagewriter = ImageWriter(A.output_dir)

    if six.PY2 and sys.stdin.encoding:
        A.password = A.password.decode(sys.stdin.encoding)

    if A.output_type == "text" and A.outfile != "-":
        for override, alttype in ((".htm", "html"), (".html", "html"),
                                  (".xml", "xml"), (".tag", "tag")):
            if A.outfile.endswith(override):
                A.output_type = alttype

    if A.outfile == "-":
        outfp = sys.stdout
        if outfp.encoding is not None:
            # Why ignore outfp.encoding? :-/ stupid cathal?
            A.codec = 'utf-8'
    else:
        outfp = open(A.outfile, "wb")

    ## Test Code
    outfp = extract_text(**vars(A))
    outfp.close()
    return 0


# convert_pdf2txt(args=[fp, '--outfile', fout, '--maxpages', str(max_page_num)])
convert_pdf2txt(args=[fp, '--outfile', fout])
with open(fout, 'r') as fp:
    text = fp.read()
    s = utils.to_unicode(text)
    text = s.replace('\n\n', '')
    # # remove nonsense character from formula
    # text = re.sub(
    #     "[^!#$%&'()*+,-./:;<=>?@[\]^_`{|}~\u4e00-\u9fa5a-zA-Z0-9\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\n\s]+",
    #     '', text)
    # # remove ^L
    # text = re.sub("\u000C", "", text)
    # # remove ( )
    # text = re.sub("[\uFF08(][^\s]+[\uFF09)]", "", text)
    # # remove following pattern 888888777777id
    # text = re.sub("[!#$%&'()*+,-./:;<=>?@[\]^_`{|}~a-zA-Z0-9]{10,}", '', text)
with open(f_parsed, 'w') as f:
    f.write(text)


def convert(args):
    pass


def convert_to_txt(args):
    pass


def convert_from(args):
    pass


for (root, dirs,
     files) in os.walk('/home/weiwu/share/deep_learning/docs/github'):
    for filename in files:
        file_path = join(root, filename)
        print(file_path)
        fout = file_path[:-3] + 'txt'
        convert_pdf2txt(args=[file_path, '--outfile', fout])
        with open(fout, 'r') as fp:
            text = fp.read()
            s = utils.to_unicode(text)
            text = s.replace('\n\n', '')
        with open(fout, 'w') as f:
            f.write(text)

re_github = re.compile('https?://github.com/[A-Za-z0-9/_-]+[\s\u000C.0-9]')
github_list = '/home/weiwu/share/deep_learning/docs/github/github_list.txt'
fout = open(github_list, 'a')
for (root, dirs,
     files) in os.walk('/home/weiwu/share/deep_learning/docs/github'):
    for filename in files:
        if filename.endswith('.txt'):
            file_path = join(root, filename)
            print(file_path)
            with open(file_path, 'r') as f:
                try:
                    out = re_github.search(f.read()).group()[:-1]
                    print(out)
                except AttributeError:
                    continue
            #with open(github_list, 'a') as fout:
            fout.write(out + os.linesep)
fout.close()
