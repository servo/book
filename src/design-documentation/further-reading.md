<!-- TODO: needs copyediting -->

# Further reading

## References

Important research and accumulated knowledge about browser implementation, parallel layout, etc.:

* [How Browsers Work](http://ehsan.github.io/how-browsers-work/#1) - basic explanation of the common design of modern web browsers by long-time Gecko engineer Ehsan Akhgari
* [More how browsers work](http://taligarsiel.com/Projects/howbrowserswork1.htm) article that is dated, but has many more details
* [Webkit overview](https://web.archive.org/web/20150804185551/https://www.webkit.org/coding/technical-articles.html)
* [Fast and parallel web page layout (2010)](https://lmeyerov.github.io/projects/pbrowser/pubfiles/paper.pdf) - Leo Meyerovich's influential parallel selectors, layout, and fonts.
  It advocates separating parallel selectors from parallel cascade to improve memory usage.
  See also the [2013 paper for automating layout](https://lmeyerov.github.io/projects/pbrowser/pubfiles/synthesizer2012.pdf) and the [2009 paper that touches on speculative lexing/parsing](http://lmeyerov.github.io/projects/pbrowser/hotpar09/paper.pdf).
* [Servo layout on mozilla wiki](https://wiki.mozilla.org/Servo/StyleUpdateOnDOMChange)
* [Robert O'Callahan's mega-presentation](http://robert.ocallahan.org/2012/04/korea.html) - Lots of information about browsers
* [ZOOMM paper](https://www.researchgate.net/publication/277679324_ZOOMM) - Qualcomm's network prefetching and combined selectors/cascade
* [Strings in Blink](https://chromium.googlesource.com/chromium/src/+/HEAD/third_party/blink/renderer/platform/wtf/text/README.md)
* [Incoherencies in Web Access Control Policies](http://research.microsoft.com/en-us/um/people/helenw/papers/incoherencyAndWebAnalyzer.pdf) - Analysis of the prevelance of document.domain, cross-origin iframes and other weirdness
* [A Case for Parallelizing Web Pages](https://www.usenix.org/system/files/conference/hotpar12/hotpar12-final58.pdf) -- Sam King's server proxy for partitioning webpages.
  See also his [process-isolation work that reports parallelism benefits](https://cseweb.ucsd.edu/~dstefan/cse291-spring21/papers/grier:op.pdf).
* [High-Performance and Energy-Efficient Mobile Web Browsing on Big/Little Systems](https://edge.seas.harvard.edu/sites/g/files/omnuum6351/files/zhu10hpca_0.pdf) Save power by dynamically switching which core to use based on automatic workload heuristic
* [C3: An Experimental, Extensible, Reconfigurable Platform for HTML-based Applications](https://web.archive.org/web/20140718031023/http://research.microsoft.com/apps/pubs/default.aspx?id=150010) Browser prototype written in C# at Microsoft Research that provided a concurrent (though not successfully parallelized) architecture
* [CSS Inline vertical alignment and line wrapping around floats](https://github.com/dbaron/inlines-and-floats) - dbaron imparts wisdom about floats
* [Quark](http://goto.ucsd.edu/quark/) - Formally verified browser kernel
* [HPar: A Practical Parallel Parser for HTML](https://web.archive.org/web/20150823220338/https://www.cs.ucr.edu/~zhijia/papers/taco13.pdf)
* [Gecko HTML parser threading](https://web.archive.org/web/20171209054744/https://developer.mozilla.org/en-US/docs/Mozilla/Gecko/HTML_parser_threading)
