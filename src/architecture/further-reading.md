<!-- TODO: needs copyediting -->

# Further reading

## References

Important research and accumulated knowledge about browser implementation, parallel layout, etc:

* [How Browsers Work](http://ehsan.github.io/how-browsers-work/#1) - basic explanation of the common design of modern web browsers by long-time Gecko engineer Ehsan Akhgari
* [More how browsers work](http://taligarsiel.com/Projects/howbrowserswork1.htm) article that is dated, but has many more details
* [Webkit overview](http://www.webkit.org/coding/technical-articles.html)
* [Fast and parallel web page layout (2010)](https://lmeyerov.github.io/projects/pbrowser/pubfiles/paper.pdf) - Leo Meyerovich's influential parallel selectors, layout, and fonts.
  It advocates seperating parallel selectors from parallel cascade to improve memory usage.
  See also the [2013 paper for automating layout](https://lmeyerov.github.io/projects/pbrowser/pubfiles/synthesizer2012.pdf) and the [2009 paper that touches on speculative lexing/parsing](http://lmeyerov.github.io/projects/pbrowser/hotpar09/paper.pdf).
* [Servo layout on mozilla wiki](https://wiki.mozilla.org/Servo/StyleUpdateOnDOMChange)
* [Robert O'Callahan's mega-presentation](http://robert.ocallahan.org/2012/04/korea.html) - Lots of information about browsers
* [ZOOMM paper](http://dl.acm.org/citation.cfm?id=2442543) - Qualcomm's network prefetching and combined selectors/cascade
* [Strings in Blink](https://docs.google.com/document/d/1kOCUlJdh2WJMJGDf-WoEQhmnjKLaOYRbiHz5TiGJl14/edit#heading=h.6w5vu5wppuew)
* [Incoherencies in Web Access Control Policies](http://research.microsoft.com/en-us/um/people/helenw/papers/incoherencyAndWebAnalyzer.pdf) - Analysis of the prevelance of document.domain, cross-origin iframes and other wierdness
* [A Case for Parallelizing Web Pages](http://www.cs.uiuc.edu/homes/kingst/Research_files/mai12.pdf) -- Sam King's server proxy for partitioning webpages.
  See also his [process-isolation work that reports parallelism benefits](http://www.cs.uiuc.edu/homes/kingst/Research_files/tang10_1.pdf).
* [High-Performance and Energy-Efficient Mobile Web Browsing on Big/Little Systems](https://webspace.utexas.edu/yz4422/hpca13.pdf) Save power by dynamically switching which core to use based on automatic workload heuristic
* [C3: An Experimental, Extensible, Reconfigurable Platform for HTML-based Applications](http://research.microsoft.com/apps/pubs/default.aspx?id=150010) Browser prototype written in C# at Microsoft Research that provided a concurrent (though not successfully parallelized) architecture
* [CSS Inline vertical alignment and line wrapping around floats](https://github.com/dbaron/inlines-and-floats) - dbaron imparts wisdom about floats
* [Quark](http://goto.ucsd.edu/quark/) - Formally verified browser kernel
* [HPar: A Practical Parallel Parser for HTML](http://www.cs.ucr.edu/~zhijia/papers/taco13.pdf)
* [Gecko HTML parser threading](https://developer.mozilla.org/en-US/docs/Mozilla/Gecko/HTML_parser_threading)
