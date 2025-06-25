<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html" doctype-system="about:legacy-compat" encoding="UTF-8" indent="yes"/>

    <xsl:template match="/movie">
        <html>
            <head>
                <title>Film Detayı: <xsl:value-of select="title"/></title>
                <style>
                    body { font-family: sans-serif; margin: 2em; }
                    .container { display: flex; gap: 20px; }
                    .poster img { max-width: 300px; box-shadow: 2px 2px 10px #ccc; }
                    .details { flex-grow: 1; }
                    h1 { color: #333; }
                    h2 { color: #555; border-bottom: 1px solid #eee; padding-bottom: 5px;}
                    .plot { font-style: italic; color: #666; }
                    .genres span, .actors span { 
                        display: inline-block; 
                        background-color: #eee; 
                        border-radius: 3px; 
                        padding: 3px 8px; 
                        margin-right: 5px;
                        margin-bottom: 5px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="poster">
                        <img src="{posterUrl}" alt="{title} Poster"/>
                    </div>
                    <div class="details">
                        <h1><xsl:value-of select="title"/> (<xsl:value-of select="year"/>)</h1>
                        <p><strong>Yönetmen:</strong> <xsl:value-of select="director"/></p>
                        <p><strong>Puan:</strong> <xsl:value-of select="rating"/> / 10</p>
                        
                        <h2>Konu</h2>
                        <p class="plot"><xsl:value-of select="plot"/></p>
                        
                        <!-- <h2>Türler</h2>
                        <div class="genres">
                            <xsl:for-each select="genres/genre">
                                <span><xsl:value-of select="."/></span>
                            </xsl:for-each>
                        </div>

                        <h2>Oyuncular</h2>
                        <div class="actors">
                            <xsl:for-each select="actors/actor">
                                <span><xsl:value-of select="."/></span>
                            </xsl:for-each>
                        </div> -->
                    </div>
                </div>
            </body>
        </html>
    </xsl:template>

</xsl:stylesheet>