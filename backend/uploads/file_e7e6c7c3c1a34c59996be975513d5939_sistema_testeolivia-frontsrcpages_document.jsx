import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang='pt-BR'>
      <Head>
        {/* Fonte Rawline do DSGov */}
        <link
          rel='stylesheet'
          href='https://cdngovbr-ds.estaleiro.serpro.gov.br/design-system/fonts/rawline/css/rawline.css'
        />
        {/* Core CSS do Design System do Governo */}
        <link
          rel='stylesheet'
          href='https://docs-ds.estaleiro.serpro.gov.br/govbr-ds-core/dist/core.min.css'
        />
        <link
          rel='stylesheet'
          href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css'
        />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
