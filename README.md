## docx->tex

Here are few files I've been using to bootstrap the TeX-ification of various Word documents. I use Word to convert from .doc to .docx, if the document is not already a .docx, then just save as normal, and run something like the following:

    ruby -Ku parse.rb -d original.docx

It's rough, and still needs a lot of work, but it's better than copy & pasting.

The output presumes that `natbib` and `amssym` and friends are within reach.

## Dependencies:

    gem install libxml-ruby

## License

Copyright Christopher Brown 2011-2012, MIT Licensed

## Acknowledgements

Developed while typesetting for [Semantics and Pragmatics](http://semprag.org/) (http://semprag.org/).



# class String
#     def apply_gsubs(sub_pairs)
#         sub_pairs.inject(self) { |str, pair| str.gsub(pair[0], pair[1]) }
#     end
# end

# class Array
#     def filter
#         self.compact.reject(&:empty?)
#     end
# end


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
            #     text = "\\begin{exe}\n\\ex[]{\\label{#{@example_counter}}#{text}}\n\\end{exe}\n"
            #     @example_counter += 1
            #     text
            elsif /^\((\d+)\)$/.match(first_fragment)
                # collapse_spans(spans.drop(1)).map { |span| span.to_s(@ignore_styles) }.join
                @example_counter += 1
                '''
                \\begin{exe}
                    \\ex[]{\\label{ex:#{$1}}
                        #{p_sequence}
                    }
                \\end{exe}
                '''
                else
                    p_sequence.to_s
                end
            else
                ''
            end
        end
