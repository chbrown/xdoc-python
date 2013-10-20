from xdoc.formats.docx.reader import parse_docx


def read(docx_fp):
    # returns a xdoc.document.Document object
    document = parse_docx(docx_fp)
    # is this the best place to normalize? yes, I think so, unless...
    #   is there any reason we may want pre-normalized spans down the line somewhere?
    document.normalize()

    # after normalizing, try to process the bibliography

    # 1) find the start of the bibliography definition by looking for
    #    a bold span that contains the word 'References' or 'Bibliography'
    span_iter = iter(document.spans)
    for span in span_iter:
        if 'bold' in span.styles and ('References' in span.text or 'Bibliography' in span.text):
            break

    bibliography_text = ''.join(span.text for span in span_iter)

            # author_re = bib_item.lastnames.join(' (?:and|&) ').gsub("\\", "\\\\\\\\")
            # regexes = {
            #     citet:         Regexp.new(author_re + '\s*\((\d{4}\w?,?\s*)+\)'),
            #     posscitet: Regexp.new(author_re + '\'s \s*\((\d{4}\w?,?\s*)+\)'),
            #     citep:         Regexp.new('\(' + author_re + ',?\s*(\d{4}\w?,?\s*)+\)'),
            #     citealt:     Regexp.new(author_re + ',?\s*(\d{4}\w?,?\s*)+')
            # }
            # regexes.each do |key, regex|
            #     @tex = @tex.gsub(regex) do |match|
            #         refs = $1.split(',').map { |year| bib_item.ref_lastnames + ":" + year }.join(',')
            #         "\\#{key}{#{refs}}"

    return document


def write():
    raise NotImplementedError('Writing .docx files is not supported')
