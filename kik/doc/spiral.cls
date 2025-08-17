% Autor: Bartosz Kostka
% Licencja: CC BY-NC-SA 4.0
%
% Modyfikacje:


\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{spiral}

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass{article}

\usepackage[a4paper, includeheadfoot, margin=40pt, footskip=\dimexpr\headsep+\ht\strutbox\relax, bmargin = \dimexpr60pt+2\ht\strutbox\relax,]{geometry}

\usepackage[utf8]{inputenc}
\usepackage{cmbright}
%\usepackage{newtxmath}
\usepackage{amsfonts, amsmath, amssymb}
\usepackage[T1]{fontenc}
\usepackage[polish]{babel}

\usepackage{multirow}
\usepackage{graphicx}
\usepackage{tabularx}
\usepackage{verbatim}
\usepackage{fancyvrb}
\usepackage{lastpage}
\usepackage{bbding}
\usepackage{tikz}
\usepackage{hyperref}
\usepackage{listings}
\usepackage{ifmtarg}


% removes section numbers
\renewcommand{\@seccntformat}[1]{}

% footer
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}


\fancyfoot[C]{
      \hrule
      \vspace{4pt}
      \begin{footnotesize}
          \begin{tabularx}{1.015\textwidth}{lXr}
          \hspace{-13pt}
          \begin{tabular}{l}\title \\ \textcopyright \ \the\year{} XIV LO im. Stanisława Staszica \\ \href{https://sio2.staszic.waw.pl}{sio2.staszic.waw.pl}\end{tabular} &
          \begin{tabular}{c}\\ Szablon treści zadania został zaadaptowany z szablonu \\ stworzonego przez Bartosza Kostkę, dostępnego pod \\ warunkami licencji CC BY-NC-SA 4.0. \end{tabular} &
          \begin{tabular}{r}\vspace{3pt} \thepage/\pageref*{LastPage} \\ \raisebox{-8pt}{\href{https://creativecommons.org/licenses/by-nc-sa/4.0/deed.pl}{\includegraphics[height=18px]{licencja}}} \end{tabular}
          \end{tabularx}
      \end{footnotesize}
}

% \lfoot{\footnotesize \title \\ XIV Olimpiada Informatyczna Juniorów \\ \href{https://oij.edu.pl}{oij.edu.pl} }
% \rfoot{\footnotesize \vspace{13pt} \thepage/\pageref*{LastPage}}
\renewcommand{\headrulewidth}{0px}
\setlength{\headheight}{0px}

\def\ifdef#1{\ifcsname#1\endcsname}

\ifdef{authorskey} \else \def\authorskey{Autor zadania} \fi

% header
\def\makeheader{%
  \raisebox{15px}{
  \hspace{-20px}
  \begin{minipage}[b][50px]{0.85\textwidth}
  \hspace{2px}
  {\LARGE \bf \title \ifdef{mode} \hspace{-8pt} \normalsize{(\mode)} \fi} \\
  \begin{small}
  \begin{tabularx}{\textwidth}{Xrl} \\
    \bf \contest &
    \ifdef{id} Kod zadania: \fi
    &
    \ifdef{id} \bf \detokenize\expandafter{\id} \fi \\
    \desc &
    \ifdef{ML} Limit pamięci: \fi
    \ifdef{setters} Opracowanie: \fi
    &
    \ifdef{ML} \bf \ML \fi
    \ifdef{setters} \bf \setters \fi \\
  \end{tabularx}
  \end{small}
  \end{minipage}
  \begin{minipage}[b][50px]{0.15\textwidth}
  \hspace{15px}\raisebox{3px}{\includegraphics[width=60px]{logo}}
  \end{minipage}
  }
  \vspace{-25px}
  \hrule
  \vspace{12px}
}

\usepackage{accsupp}
\newcommand{\noncopynumber}[1]{%
    \BeginAccSupp{method=escape,ActualText={}}%
    #1%
    \EndAccSupp{}%
}

\definecolor{codegreen}{rgb}{0,0.6,0}
\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{backcolour}{rgb}{0.95,0.95,0.92}

\lstset{
  keywordstyle=\bfseries\color{magenta},
  numberstyle=\tiny\color{codegray},
  stringstyle=\color{codepurple},
  frame=none,
  breaklines=true,
  inputencoding=utf8,
  extendedchars=true,
  numberstyle=\footnotesize,
  texcl=true,
  backgroundcolor=\color{backcolour},
  columns=fullflexible,
  commentstyle=\color{codegreen},
  xleftmargin=4.5em,
  framexleftmargin=3em,
  showstringspaces=true,
  numbers=left,
  keepspaces=true,
  basicstyle=\small\fontfamily{fvm}\selectfont,
}

\newcommand\includecode[2]{
  \vspace{-0.7em}
  \lstinputlisting[#1]{#2}
}

\newcommand\includefile[1]{
  \vspace{-0.7em}
  \VerbatimInput[frame=single]{#1}
}

\newcommand\example[1]{
  \begin{center}%
  \begin{minipage}[t]{0.45\textwidth}%
  \vspace{0pt}%
      \noindent Wejście dla testu {\tt \detokenize\expandafter{\id}#1}:%
      \includefile{../in/\id#1.in}%
  \end{minipage}\hfill%
  \begin{minipage}[t]{0.1\textwidth}%
  \end{minipage}%
  \begin{minipage}[t]{0.45\textwidth}%
  \vspace{0pt}%
      \noindent Wyjście dla testu {\tt \detokenize\expandafter{\id}#1}:%
      \includefile{../out/\id#1.out}
  \end{minipage}%
  \end{center}%
}

\newcommand\fullexample[1]{
  \noindent Wejście dla testu {\tt \detokenize\expandafter{\id}#1}:%
  \includefile{../in/\id#1.in}%

  \noindent Wyjście dla testu {\tt \detokenize\expandafter{\id}#1}:%
  \includefile{../out/\id#1.out}
}

\newcommand\note[1]{
  \noindent {\bf Wyjaśnienie do przykładu:} #1
}

\newenvironment{ocen}{%
  \subsection{Pozostałe testy przykładowe}
  \begin{itemize}
}{
  \end{itemize}
}%

\newcommand\testocen[2]{
   \item[-] test {\tt \id#1}: #2
}

\newenvironment{subtasks}{
\tabularx{\textwidth}{|c|X|c|c|}
\hline
\textbf{Podzadanie} & \textbf{Ograniczenia} & \textbf{Limit czasu} & \textbf{Liczba punktów}\\
\hline
}{
\endtabularx
}

\newcommand\subtask[4]{
  #1 & #2 & #3 & #4\\ \hline
}

\newcommand\twocol[2]{%
\begin{center}%
\begin{minipage}[t]{0.5\textwidth}%
\vspace{0pt}%
{#1}%
\end{minipage}\hfill%
\begin{minipage}[t]{0.5\textwidth}%
\vspace{0pt}%
{#2}%
\end{minipage}%
\end{center}}
