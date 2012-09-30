# MIT Licensed, (c) 2011 Christopher Brown

require 'rubygems'
require 'optparse'
require 'xml'
require 'zip/zip'

require './chars' # ACCENT_REPLACEMENTS, CHAR_SYMS
require './bib' # BibItem

class String
  def apply_gsubs(sub_pairs)
    sub_pairs.inject(self) { |str, pair| str.gsub(pair[0], pair[1]) }
  end
end

class Array
  def filter
    self.compact.reject(&:empty?)
  end
end

class Span
  attr_accessor :fragments, :emph, :textbf, :subscript, :superscript
  def initialize(fragments)
    @fragments = fragments
    @emph = @textbf = @subscript = @superscript = false
  end
  def to_s(ignore_styles=false)
    tex = @fragments.join
    if !ignore_styles
      pre = tex.match(/^\s+/)
      post = tex.match(/\s+$/)
      tex = tex.strip
      tex = "\\emph{#{tex}}" if @emph
      tex = "\\textbf{#{tex}}" if @textbf
      tex = "^{#{tex}}" if @superscript
      tex = "_{#{tex}}" if @subscript
      tex = pre[0] + tex if pre
      tex = tex + post[0] if post
    end
    tex
  end
end

class Sequence
  attr_accessor :spans

  def initialize
    @spans = []
  end

  def add(span)
    top = @spans.last
    # def props_equal?(other)
      # other.emph.nil? == @emph.nil? and other.textbf.nil? == @textbf.nil? and
        # other.subscript.nil? == @subscript.nil? and other.superscript.nil? == @superscript.nil?
    # end

    mergeable = !top.nil? && [:emph, :textbf, :subscript, :superscript].all? { |sym| top.send(sym).nil? == span.send(sym).nil? }
    if mergeable
      top.fragments += span.fragments
    else
      @spans << span
    end
  end

  def empty?
    @spans.empty?
  end

  def to_s(ignore_styles=false)
    @spans.map { |span| span.to_s(ignore_styles) }.join
  end
end

class Document
  attr_accessor :bibliography

  def read_notes(doc)
    Hash[doc.find('//w:footnote | //w:endnote').map { |note_node|
      text = note_node.find('w:p').map do |p_node|
        read_p(p_node).strip
      end.filter.join("\n")
      [note_node.attributes['id'], text]
    }]
  end

  def initialize(docx_filepath)
    @tex = ''
    @bibliography = []
    @bibliography_mode = false
    @example_counter = 0
    # @ignore_numPr = false
    @ignore_styles = false

    Zip::ZipFile.open(docx_filepath) do |docx_zip|
      docx_zip.each { |entry| puts entry.name }

      footnotes_xml = docx_zip.read('word/footnotes.xml')
      footnotes_doc = XML::Document.string(footnotes_xml)
      @footnotes = read_notes(footnotes_doc)

      begin
        endnotes_xml = docx_zip.read('word/endnotes.xml')
        endnotes_doc = XML::Document.string(endnotes_xml)
        @endnotes = read_notes(endnotes_doc)
      rescue
        @endnotes = {}
      end

      document_xml = docx_zip.read('word/document.xml')
      document_doc = XML::Document.string(document_xml)
      # puts document_doc
      read_body(document_doc)
    end

    interpolate_bibliography
    postprocess
  end

  def to_s
    @tex
  end

  def postprocess
    # fix latex quotes for reasonably-sized strings
    @tex = @tex.gsub(/"(.{1,100}?)"/, '``\1\'\'')
    @tex = @tex.gsub(/(\s)'(\S[^']{1,100}\S)'([.,?;\s])/, '\1`\2\'\3')
    
    # replace §1.1 with \ref{sec:1.1}
    @tex = @tex.gsub(/§+(\d+\.?\d*\.?\d*\.?\d*\.?)/) do |s|
      numbering = $1.chomp('.')
      "\\ref{sec:#{numbering}}"
    end
    
    # replace (14b) with (\ref{14b})
    @tex = @tex.gsub(/\((\d{1,2}[a-j]?)\)/) do |m|
      numbering = $1
      "(\\ref{ex:#{numbering}})"
    end
  end

  def read_r(r_node)
    # returns a list of spans, perhaps empty
    if r_node.find_first('w:t')
      # clean fragments
      fragments = r_node.find('w:t').map do |t_node|
        t_node.content.apply_gsubs(ACCENT_REPLACEMENTS)
      end

      span = Span.new(fragments)
      span.emph = r_node.find_first('w:rPr/w:i')
      span.textbf = r_node.find_first('w:rPr/w:b')
      span.subscript = r_node.find_first("w:rPr/w:vertAlign[@w:val='subscript']") ||
        r_node.find_first("w:rPr/w:position[@w:val='-4']")
      span.superscript = r_node.find_first("w:rPr/w:vertAlign[@w:val='superscript']") ||
        r_node.find_first("w:rPr/w:position[@w:val='6']")
    elsif ref = r_node.find_first('w:footnoteReference')
      footnote_id = @footnotes[ref['id']]
      span = Span.new(["\\footnote{#{footnote_id}}"])
    elsif ref = r_node.find_first('w:endnoteReference')
      endnote_id = @endnotes[ref['id']]
      # xxx: convert to footnote
      span = Span.new(["\\footnote{#{endnote_id}}"])
    elsif symNode = r_node.find_first('w:sym')
      char = symNode.attributes['char']
      if CHAR_SYMS[char]
        span = Span.new([CHAR_SYMS[char]])
      else
        span = Span.new(["XXX: WTF MISSING SYMBOL " + char.unpack('U').map(&:to_s)])
        puts span
      end
    else
      return []
    end
    return [span]
  end

  def read_body(doc)
    doc.find('//w:body/w:p').each do |body_p_child|
      p_span = read_p(body_p_child)
      if @bibliography_mode
        bib_item = BibItem.new(p_span)
        if !bib_item.fields.nil?
          @bibliography << bib_item
        end
        if /Appendix/.match(p_span)
          @bibliography_mode = false
        end
      else
        @tex += "#{p_span}\n"
        # removed $ from /^\s*References\s*$/
        @bibliography_mode = /^\s*References\s*/.match(p_span) || /^\s*(\\textbf\{)?Bibliography(\})?:?\s*$/.match(p_span)
      end
    end
  end

  def read_p(p_node)
    # returns a possibly empty string
    p_sequence = Sequence.new
    p_node.find('w:r').each do |r_node|
      read_r(r_node).each do |r_span|
        p_sequence.add(r_span)
      end
    end
    first_span = p_sequence.spans[0]
    if first_span
      first_fragment = first_span.fragments[0]

      if /^\s*§(\d+\.?\d*\.?\d*\.?\d*\.?)\s*(.*)$/.match(first_fragment)
        # $1 refers to the ^ or \textbf{, $2 refers to the original (sub)section numbering, $3 refers to the (sub)section title
        # contents.gsub!(/(^|^\\textbf\{)(\d+\.?\d*\.?\d*)\s*(.*)$/, '\subsubsection{\1\3} % \2')
        # must be first w:r of the w:p
        numbering = $1.chomp('.')
        section_text = $2
        subs = 'sub' * numbering.scan(/\./).length
        "\\#{subs}section{#{section_text}} \\label{sec:#{numbering}}"
      # elsif p_node.find_first("w:pPr/w:numPr[@w:val='1']") and !ignore_numPr
      #   text = "\\begin{exe}\n\\ex[]{\\label{#{@example_counter}}#{text}}\n\\end{exe}\n"
      #   @example_counter += 1
      #   text
      elsif /^\((\d+)\)$/.match(first_fragment)
        # collapse_spans(spans.drop(1)).map { |span| span.to_s(@ignore_styles) }.join
        @example_counter += 1
        <<EOS
\\begin{exe}
  \\ex[]{\\label{ex:#{$1}}
    #{p_sequence}
  }
\\end{exe}
EOS
      else
        p_sequence.to_s
      end
    else
      ''
    end
  end

  def interpolate_bibliography
    @bibliography.each do |bib_item|
      author_re = bib_item.lastnames.join(' (?:and|&) ').gsub("\\", "\\\\\\\\")
      regexes = {
        citet:     Regexp.new(author_re + '\s*\((\d{4}\w?,?\s*)+\)'),
        posscitet: Regexp.new(author_re + '\'s \s*\((\d{4}\w?,?\s*)+\)'),
        citep:     Regexp.new('\(' + author_re + ',?\s*(\d{4}\w?,?\s*)+\)'),
        citealt:   Regexp.new(author_re + ',?\s*(\d{4}\w?,?\s*)+')
      }
      regexes.each do |key, regex|
        @tex = @tex.gsub(regex) do |match|
          refs = $1.split(',').map { |year| bib_item.ref_lastnames + ":" + year }.join(',')
          "\\#{key}{#{refs}}"
        end
      end
    end
  end
end

options = {}
OptionParser.new do |opts|
  opts.banner = "Usage: parse.rb -d word.docx"

  opts.on("-d", "--docx Document.docx", "Your Word document original docx file") do |docx_filepath|
    options[:docx_filepath] = docx_filepath
  end
  opts.on("-t", "--tex [Output.tex]", "Destination file (will be overwritten)") do |tex_filepath|
    options[:tex_filepath] = tex_filepath
  end
end.parse!
options[:tex_filepath] ||= options[:docx_filepath].gsub(/docx/, 'tex')
options[:bib_filepath] = options[:tex_filepath].gsub(/tex/, 'bib')

puts "Reading #{options[:docx_filepath]} into #{options[:tex_filepath]} and #{options[:bib_filepath]}."
doc = Document.new(options[:docx_filepath])
IO.write(options[:tex_filepath], doc)
IO.write(options[:bib_filepath], doc.bibliography.map(&:to_s).join(''))
