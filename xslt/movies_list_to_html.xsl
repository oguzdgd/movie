<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html" doctype-system="about:legacy-compat" encoding="UTF-8" indent="yes"/>

 
    <xsl:template match="/movies">
        <html>
            <head>
                <title>Tüm Filmler</title>
                <style>
                    body { font-family: sans-serif; margin: 2em; background-color: #f8f9fa; }
                    h1 { color: #343a40; text-align: center; margin-bottom: 1em; }
                    ul { list-style-type: none; padding: 0; max-width: 800px; margin: 0 auto; }
                    li { 
                        background: #ffffff; 
                        margin-bottom: 8px; 
                        padding: 12px 20px; 
                        border-radius: 5px; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                        transition: transform 0.2s ease-in-out;
                    }
                    li:hover {
                        transform: scale(1.02);
                    }
                    a { 
                        text-decoration: none; 
                        color: #0056b3; 
                        font-weight: bold; 
                        font-size: 1.1em;
                    }
                    a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <h1>Film Kataloğu</h1>
                <ul>
                    
                    <xsl:for-each select="movie">
                    
                        <xsl:sort select="title"/>
                        <li>
                        
                            <a href="/api/v1/html/movies/{@id}/">
                                <xsl:value-of select="title"/>
                            </a>
                        </li>
                    </xsl:for-each>
                </ul>
            </body>
        </html>
    </xsl:template>

</xsl:stylesheet>