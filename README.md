## docx->tex

Here are few files I've been using to bootstrap the TeX-ification of various Word documents. I use Word to convert from .doc to .docx, if the document is not already a .docx, then just save as normal, and run something like the following:

    ruby -Ku parse.rb -d original.docx

It's rough, and still needs a lot of work, but it's better than copy & pasting.

The output presumes that `natbib` and `amssym` and friends are within reach.

## License

Copyright Christopher Brown 2011-2012, MIT Licensed
