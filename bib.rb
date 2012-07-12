# MIT Licensed, (c) 2011 Christopher Brown

re_authors = '(?<authors>.+?)\s*(?<editor>\(ed(itor)?s\.?\)\s+)?\s*'
re_editors = '(?<editor>.+?)\s*\(ed(itor)?s?\.?\)\s*'
re_year = '\((?<year>(\d{4}\w?/?)+)\)\s*'
re_title = '(?<title>[^.]+)\.\s*'
re_title_i = '\\\\emph\{(?<title>.+?)\}[.,]?\s*'
re_journal = '\\\\emph\{(?<journal>.+?)\}\.?\s*'
re_page = '(?<page_begin>\d+)-(?<page_end>\d+)'
re_vol = '((Volume)?\s*(?<volume>\d+(\.\d+)?):?\s*' + re_page + ')?'
re_pub_address = '(?<publisher>[^,]+)([.,]|, (?<address>.*[^.])[.,]?)\s*'

BIB_REGEXES = [
  # Berman, Steve (1991) \emph{On the Semantics and Logical Form of Wh-Clauses}. Ph.D. dissertation, University of Massachusetts at Amherst.
  {
    :tag => 'phdthesis',
    :re => Regexp.new(re_authors + re_year + re_title_i + 'Ph.D. dissertation, (?<school>.+)\.')
  },
  # von Fintel, Kai (1995) A minimal theory of adverbial quantification. Ms., MIT, Cambridge, MA.
  {
    :tag => 'unpublished',
    :re => Regexp.new(re_authors + re_year + re_title + 'Ms\., ' + re_pub_address),
    :fields => { :note => "Manuscript" }
  },
  # Beckman, Mary E., and Janet Pierrehumbert (1986) Intonational structure in Japanese and English. \emph{Phonology Yearbook} 3:15-70.
  {
    :tag => 'article',
    :re => Regexp.new(re_authors + re_year + re_title + re_journal + re_vol)
  },
  # Bratman, Michael E. (1987) \emph{Intentions, Plans, and Practical Reason}. Harvard University Press, Cambridge, MA.
  {
    :tag => 'book',
    :re => Regexp.new(re_authors + re_year + re_title_i + re_pub_address)
  },
  # B\"uring, Daniel (1994) Topic. In Bosch & van der Sandt (1994), Volume 2: 271-280.
  {
    :tag => '...?',
    :re => /xyzxyzxyz/
  },
  # Krifka, Manfred (1992) A compositional semantics for multiple focus constructions.  In Joachim Jacobs (ed.) \emph{Informationsstruktur und Grammatik}. Westdeutscher Verlag, Weisbaden, Germany, 17-53.
  # Roberts, Craige (1995b) Anaphora in intensional contexts. In Shalom Lappin (ed.) \emph{Handbook of Semantics}. Blackwell, London.
  {
    :tag => 'inbook',
    :re => Regexp.new(re_authors + re_year + re_title + 
      'In ' + re_editors + re_title_i + re_pub_address + '(' + re_page + ')?'),
  },
  {
    :tag => 'article',
    :re => Regexp.new(re_authors + re_year + '.*' + '\\\\emph\{(?<title>.+?)\}' + '.*'),
    :note => 'FIXME'
  }
]

class BibItem
  attr_accessor :fields, :ref_lastnames
  # , :note, :authors
  # :raw, :ref_lastnames, :ref, :type, 
  # , :year, :title, :publisher, :note

  # author = {#{authors.join(' and ')}},
  # year = {#{year}},
  # title = {#{title}},
  # publisher = {#{publication}},
  # note = {#{misc}},
  
  def initialize(raw)
    @raw = raw
    BIB_REGEXES.each do |bib_regex|
      match = bib_regex[:re].match(raw)
      if match
        parse(bib_regex, match)
        # contents = "  [\"#{last_names.join(' and ').gsub("\\", "\\\\\\\\")}\", '#{year}', '#{id}'],\n"
        break
      end
    end
  end
    
  def parse(bib_regex, match)
    @fields = bib_regex[:fields] || {}
    @type = bib_regex[:tag]
    @note = bib_regex[:note] ? bib_regex[:note] + "\n" : ''

    authors = match[:authors].split(/,?\s*?(?:\band\b|&)/).map { |author| author.split(/,\s*/, 2).reverse.join(' ').strip }
    last_names = authors.map { |author| author.split[-1] }
    @ref_lastnames = last_names.join('-').downcase.gsub(/\W/, '')
    year = match[:year]
    @ref = @ref_lastnames + ":" + (year ? year.strip : '')
    @authors = authors
    @fields[:author] = authors.join(' and ')
  
    # \((\d{4}\w?,?)+\)/

    processed_names = ['authors', 'page_begin', 'page_end']
    match.names.each do |match_name|
      unless processed_names.include?(match_name)
        match_val = match[match_name]
        unless match_val == '' or match_val.nil?
          @fields[match_name] = match_val
        end
      end
    end

    if match.names.include?('page_begin') and match.names.include?('page_end') and 
        match[:page_begin] and match[:page_end]
      @fields[:pages] = "#{match[:page_begin]}--#{match[:page_end]}" 
    end
  end
  
  def lastnames
    @authors.map do |author|
      if author.split[-2][0] == 'v'
        author.split[-2..-1].join(' ')
      else
        author.split[-1]
      end
    end
  end
 
  def to_s
    fields_string = fields.to_a.map { |key, val| "#{key} = {#{val}}" }.join(",\n  ")
    <<EOS
#{@note}#{@raw}
@#{@type}{#{@ref},
  #{fields_string}
}
EOS
  end
end
