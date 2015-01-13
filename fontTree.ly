date = #(strftime "%d-%m-%Y" (localtime (current-time)))
\header {
     title = \markup {
         \override #'(font-name . "Futura")
         "Moses All"

     }
     
     subtitle = \markup {
     	\override #'(font-name . "Futura")
     	{for Tiffany Ng}}
     
     opus = \markup {
         \override #'(font-name . "Futura")
         "J. R. Treviño (2013)"
     }
     tagline = \markup {
         \override #'(font-name . "Futura")
         \fontsize #-3.5
         {
             Engraved on \date using \with-url #"http://lilypond.org/"
             { LilyPond \simple #(lilypond-version) (http://lilypond.org/) }
         } 
     }
}

