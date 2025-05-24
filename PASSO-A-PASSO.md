Vou iniciar o projeto fazendo a extração do produto. Primeiro checo se os dados do produto vem de alguma api, porém o site é completamente renderizado no lado do servidor, isso é vantajoso pois significa que o custo para o scraping será menor, pois não precisaremos de nenhuma tecnologias para emular um browser, pois geralmente sites que buscam informações com javascript, são todos contruidos com javascript, o que dificulta o scraping. Ambos tem suas desvantagens, a maior desvantagem do serverside é que apesar de ser mais simples buscar o conteúdo, é mais trabalhoso extrair dados relevantes no html do que em um arquivo json. E é mais instável, pois qualquer mudança no layout pode impactar o scraping.

Consegui fazer uma requisição para a página do produto que vou usar como cobaia para meus testes: CEBM3615T-D.

A requisição para a página do produto parece não ter nenhum tipo de proteção a não ser uma verificação de agents, ao fazer uma requisição ela ficou rodando indefinidamente, porém ao setar um agent, ela passou normalmente. Então a fim de manter as coisas simples, irei continuar as requisições apenas usando a biblioteca requests.

Feito a requisição, agora basta extrair os dados do html, os dados podem estar contidos em metatags ou elementos visuais. Agora é buscar estes dados, atráves de uma busca com o devtools do navegador e ir testando os seletores mais estáveis possíveis que podemos usar.

Encontrei o código, descrição, imagem principal, ship_weight, e upc inicialmente, não foi uma tarefa complicada.

Agora vamos para a segunda fase, percebi que os detalhes do produto está num componente de tab, vou começar pelo specs. Como são muitos itens, não faz sentido buscar pelo nome de um por um. Vou buscar um seletor que abranja todos os itens de detalhes, e transforme o nome e valor em uma propriedade/valor como um objeto python. Os valores que aparecem como none, eu automaticamente transformei no valor None do python, para facilitar caso queiramos fazer algum tipo de tratamento depois, como transformar em um json.

Vamos agora para o drawings. Percebi que esta tab tem um botão de download, a primeira vista imaginei que seria necessário usar um navegador, mas considerando que o custo e complexidade para extração sempre é eleveado nesses casos, dei uma olhada a mais no código, e encontrei uma seção que contém todos os links de downloads:
Em .section.cadfiles, vou pegar todo o array de dados e jogar no dict produto.

Percebi que a url que existe no array, não é a mesma que eu vejo na aba networks do devtools ao clicar em "download". A url que aparece no html, é uma url interna, que não é acessível em uma rede externa, então pelo que é possível visualizar na url da aba networks, é feita uma requisição para uama url pública do site,e passamos como parametro a url interna,, ela funciona como um proxy para baixar os arquivos, nesse caso vou criar uma função para converter esta url e trazer a lista de arquivos com a url final.

Agora, falta extrair as imagens "Dimension Sheet" e "Connection Diagram":
Ela está renderizada como várias divs no devtools, porém no html puro que recebo do requests, ele esta no formato de renderização de listas do angular, nesse caso vou utilizar a mesma estrátegia dos cad_files, e buscar o local de onde o angular esta puxando esses dados, encontrei na mesma section que os cad_files, então aproveitei o código anterior para buscar também essa lista de drawnings. Porém esta visualização de lista em angular usa muito javascript e muito não está visível diretamente no html. Para resolver isso baixei toda página deste produto, juntamente com o javascript e todos os arquivos que são puxados a partir do html. Fazendo uma busca encontrei todos os itens que preciso, como exemplo a função "getDrwKindName" que é usada para dar um nome ao drawing a partir do "kind", vou transformar esses itens javascript para código python para fazer a transformação nosso scrapper que o site faria no javascript. Feito isso basta gerar a url da imagem que é construída usando o id do produto + id do material.

A próxima tab agora é "Nameplate", está dentro de uma tabela de classe "nameplate" e é renderizado no servidor, então podemos coletar os dados sem problemas usando o mesmo método dos casos anteriores.

A tab agora é "performance", ela contém tabelas de métricas de desempenho do produto em diferentes voltagens. Ela fica dentro da pane de atributo "data-tab="performance" e cada situação tem início com um título do tipo (<h2>Performance at 460 V, 60 Hz, 5 hp</h2>), para buscar as informações de cada métrica, vamos pegar os dados desde este titúlo até o próximo, assim conseguimos separar os dados para cada voltagem.

```json
{ "460": {}, "230": {} }
```

Agora a última tab "PARTS", o conteúdo desta tab é uma tabela simples, vai ser rápido.

Finalizado a extração das partes mais relevantes da página a respeito do produto, agora temos um json neste formato:

```json
{
  "code": "CEBM3615T-D",
  "description": "5HP, 1750RPM, 3PH, 60HZ, 184TC, 3642M, TEFC, F1",
  "image": "https://www.baldor.com/api/images/536",
  "ship_weight": "121.000 LB",
  "upc": "781568541739",
  "specs": {
    "Catalog Number": "CEBM3615T-D",
    "Enclosure": "TEFC",
    "Frame": "184TC",
    "Frame Material": "Steel",
    "Frequency": "60.00 Hz",
    "Motor Letter Type": "Three Phase",
    "Output @ Frequency": "5.000 HP @ 60 HZ",
    "Phase": "3",
    "Synchronous Speed @ Frequency": "1800 RPM @ 60 HZ",
    "Voltage @ Frequency": "460.0 V @ 60 HZ",
    "Haz Area Class and Group": null,
    "Haz Area Division": "Not Applicable",
    "Agency Approvals": "CURUSEEV",
    "Ambient Temperature": "40 °C",
    "Auxillary Box": "No Auxillary Box",
    "Auxillary Box Lead Termination": null,
    "Base Indicator": "Rigid",
    "Bearing Grease Type": "Polyrex EM (-20F +300F)",
    "Blower": null,
    "Brake Torque": "25.0 lb-ft",
    "Current @ Voltage": "13.900 A @ 208.0 V",
    "Design Code": "B",
    "Drip Cover": "No Drip Cover",
    "Duty Rating": "CONT",
    "Efficiency @ 100% Load": "89.5 %",
    "Electrically Isolated Bearing": "Not Electrically Isolated",
    "Feedback Device": "NO FEEDBACK",
    "High Voltage Full Load Amps": "6.7 a",
    "Front Face Code": "Fan Housing Cover For Brake",
    "Front Shaft Indicator": null,
    "Heater Indicator": "No Heater",
    "Insulation Class": "F",
    "Inverter Code": "Inverter Ready",
    "KVA Code": "J",
    "Lifting Lugs": "Standard Lifting Lugs",
    "Locked Bearing Indicator": "Locked Bearing",
    "Motor Lead Exit": "Ko Box",
    "Motor Lead Termination": "Flying Leads",
    "Motor Lead Quantity/Wire Size": "9 @ 16 AWG",
    "Motor Type": "3642M",
    "Mounting Arrangement": "F1",
    "Number of Poles": "4",
    "Overall Length": "23.13 IN",
    "Power Factor": "78",
    "Product Family": "General Purpose",
    "Product Type": "D-SERIES BRAKE MOTORS",
    "Pulley End Bearing Type": "Ball",
    "Pulley Face Code": "C-Face",
    "Pulley Shaft Indicator": "Standard",
    "Rodent Screen": null,
    "Service Factor": "1.15",
    "Shaft Diameter": "1.125 IN",
    "Shaft Extension Location": "Pulley End",
    "Shaft Ground Indicator": "No Shaft Grounding",
    "Shaft Rotation": "Reversible",
    "Shaft Slinger Indicator": "No Slinger",
    "Speed": "1750 rpm",
    "Speed Code": "Single Speed",
    "Motor Standards": "NEMA",
    "Starting Method": "Direct on line",
    "Thermal Device - Bearing": null,
    "Thermal Device - Winding": null,
    "Vibration Sensor Indicator": "No Vibration Sensor",
    "Winding Thermal 1": null,
    "Winding Thermal 2": null
  },
  "cad_files": [
    {
      "name": "2D AutoCAD DWG >=2000",
      "value": "36LYM650_23.14.DWG",
      "version": "",
      "filetype": "2D",
      "url": "https://www.baldor.com/api/products/download/?value=36LYM650_23.14.DWG&url=http%3A%2F%2FUSFSM-S-HQDMS02.baldor.abb.com%3A1090%2FContentServer%2FContentServer.dll%3Fget%26pVersion%3D0046%26contRep%3DZMARKETING%26docId%3D02063300001C1EE58196499E4069BE98%26compId%3D36LYM650_23.14.DWG"
    },
    {
      "name": "2D AutoCAD DXF >=2000",
      "value": "36LYM650_23.14.DXF",
      "version": "",
      "filetype": "2D",
      "url": "https://www.baldor.com/api/products/download/?value=36LYM650_23.14.DXF&url=http%3A%2F%2FUSFSM-S-HQDMS02.baldor.abb.com%3A1090%2FContentServer%2FContentServer.dll%3Fget%26pVersion%3D0046%26contRep%3DZMARKETING%26docId%3D02063300001C1EE58196499E406ADE98%26compId%3D36LYM650_23.14.DXF"
    },
    {
      "name": "3D ACIS",
      "value": "36LYM650_23.14.sat",
      "version": "",
      "filetype": "3D",
      "url": "https://www.baldor.com/api/products/download/?value=36LYM650_23.14.sat&url=http%3A%2F%2FUSFSM-S-HQDMS02.baldor.abb.com%3A1090%2FContentServer%2FContentServer.dll%3Fget%26pVersion%3D0046%26contRep%3DZMARKETING%26docId%3D02063300000C1EE581965947E4DA9254%26compId%3D36LYM650_23.14.sat"
    },
    {
      "name": "3D Catia",
      "value": "36LYM650_23.14.cgr",
      "version": "",
      "filetype": "3D",
      "url": "https://www.baldor.com/api/products/download/?value=36LYM650_23.14.cgr&url=http%3A%2F%2FUSFSM-S-HQDMS02.baldor.abb.com%3A1090%2FContentServer%2FContentServer.dll%3Fget%26pVersion%3D0046%26contRep%3DZMARKETING%26docId%3D02063300000C1EE5819659734E341254%26compId%3D36LYM650_23.14.cgr"
    },
    {
      "name": "3D IGES",
      "value": "36LYM650_23.14.IGS",
      "version": "",
      "filetype": "3D",
      "url": "https://www.baldor.com/api/products/download/?value=36LYM650_23.14.IGS&url=http%3A%2F%2FUSFSM-S-HQDMS02.baldor.abb.com%3A1090%2FContentServer%2FContentServer.dll%3Fget%26pVersion%3D0046%26contRep%3DZMARKETING%26docId%3D02063300000C1EE5819656DDDDF23254%26compId%3D36LYM650_23.14.IGS"
    },
    {
      "name": "3D Parasolid X_B",
      "value": "36LYM650_23.14.x_b",
      "version": "",
      "filetype": "3D",
      "url": "https://www.baldor.com/api/products/download/?value=36LYM650_23.14.x_b&url=http%3A%2F%2FUSFSM-S-HQDMS02.baldor.abb.com%3A1090%2FContentServer%2FContentServer.dll%3Fget%26pVersion%3D0046%26contRep%3DZMARKETING%26docId%3D02063300000C1EE58196581C019A9254%26compId%3D36LYM650_23.14.x_b"
    },
    {
      "name": "3D SOLIDWORKS 2014",
      "value": "36LYM650_23.14.sldprt",
      "version": "",
      "filetype": "3D",
      "url": "https://www.baldor.com/api/products/download/?value=36LYM650_23.14.sldprt&url=http%3A%2F%2FUSFSM-S-HQDMS02.baldor.abb.com%3A1090%2FContentServer%2FContentServer.dll%3Fget%26pVersion%3D0046%26contRep%3DZMARKETING%26docId%3D02063300001C1EE58196499E40689E98%26compId%3D36LYM650_23.14.sldprt"
    },
    {
      "name": "3D STEP",
      "value": "36LYM650_23.14.STEP",
      "version": "",
      "filetype": "3D",
      "url": "https://www.baldor.com/api/products/download/?value=36LYM650_23.14.STEP&url=http%3A%2F%2FUSFSM-S-HQDMS02.baldor.abb.com%3A1090%2FContentServer%2FContentServer.dll%3Fget%26pVersion%3D0046%26contRep%3DZMARKETING%26docId%3D02063300000C1EE5819657D6C8BAD254%26compId%3D36LYM650_23.14.STEP"
    }
  ],
  "drawings": [
    {
      "number": "36LYM650",
      "kind": "Dimension Sheet",
      "image_url": "https://www.baldor.com/api/products/CEBM3615T-D/drawings/36LYM650",
      "kind_id": 0,
      "material": null,
      "description": null,
      "url": null,
      "type": null,
      "revision": null
    },
    {
      "number": "CD0005",
      "kind": "Connection Diagram",
      "image_url": "https://www.baldor.com/api/products/CEBM3615T-D/drawings/CD0005",
      "kind_id": 1,
      "material": null,
      "description": null,
      "url": null,
      "type": null,
      "revision": null
    },
    {
      "number": "CD2120",
      "kind": "Connection Diagram",
      "image_url": "https://www.baldor.com/api/products/CEBM3615T-D/drawings/CD2120",
      "kind_id": 1,
      "material": null,
      "description": null,
      "url": null,
      "type": null,
      "revision": null
    }
  ],
  "nameplate": {
    "CAT.NO.": "CEBM3615T-D",
    "SPEC.": "36M650S268G1",
    "HP": "5",
    "VOLTS": "230/460",
    "AMP": "13.4/6.7",
    "RPM": "1750",
    "FRAME": "184TC",
    "HZ": "60",
    "PH": "3",
    "SER.F.": "1.15",
    "CODE": "J",
    "DES": "B",
    "CL": "F",
    "NEMA-NOM-EFF": "89.5",
    "PF": "78",
    "RATING": "40C AMB-CONT",
    "CC": "010A",
    "DE": "6206",
    "ODE": "6205",
    "ENCL": "TEFC"
  },
  "performance": {
    "460 V, 60 Hz, 5 hp": {
      "general_characteristics": {
        "Full Load Torque": "0 LB-FT",
        "No-Load Current": "0 A",
        "Line-Line Res. @ 25° C": "2.27 Ohms A Ph / 0 Ohms B Ph",
        "Temp. Rise @ Rated Load": "71° C",
        "Temp. Rise @ S.F. Load": "87° C",
        "Start Configuration": "DOL",
        "Break-Down Torque": "52.2 LB-FT",
        "Pull-Up Torque": "31.5 LB-FT",
        "Locked-Rotor Torque": "34.9 LB-FT",
        "Starting Current": "49.1 A"
      },
      "load_characteristics": {
        "Power Factor": {
          "Rated Load": "6.0",
          "0%": "39.0",
          "25%": "60.0",
          "50%": "72.0",
          "75%": "78.0",
          "100%": "83.0",
          "125%": "83.0",
          "150%": "81.0",
          "S.F.": null
        },
        "Efficiency": {
          "Rated Load": "0.0",
          "0%": "85.0",
          "25%": "89.7",
          "50%": "90.6",
          "75%": "89.6",
          "100%": "88.6",
          "125%": "87.0",
          "150%": "89.0",
          "S.F.": null
        },
        "Speed (RPM)": {
          "Rated Load": "1,799",
          "0%": "1,789",
          "25%": "1,776",
          "50%": "1,762",
          "75%": "1,750",
          "100%": "1,733",
          "125%": "1,714",
          "150%": "1,740",
          "S.F.": null
        },
        "Line Amps": {
          "Rated Load": "3.24",
          "0%": "3.55",
          "25%": "4.31",
          "50%": "5.43",
          "75%": "6.65",
          "100%": "7.94",
          "125%": "9.64",
          "150%": "7.42",
          "S.F.": null
        }
      },
      "performance_curves": {
        "image_url": "https://www.baldorvip.com/Drawing/ACPerformance?productNumber=CEBM3615T-D&recordId=35063"
      }
    },
    "230 V, 60 Hz, 5 hp": {
      "general_characteristics": {
        "Full Load Torque": "0 LB-FT",
        "No-Load Current": "0 A",
        "Line-Line Res. @ 25° C": "0.567 Ohms A Ph / 0 Ohms B Ph",
        "Temp. Rise @ Rated Load": "71° C",
        "Temp. Rise @ S.F. Load": "86° C",
        "Start Configuration": "DOL",
        "Break-Down Torque": "52.2 LB-FT",
        "Pull-Up Torque": "31.5 LB-FT",
        "Locked-Rotor Torque": "34.9 LB-FT",
        "Starting Current": "98.2 A"
      },
      "load_characteristics": {
        "Power Factor": {
          "Rated Load": "6.0",
          "0%": "38.0",
          "25%": "60.0",
          "50%": "72.0",
          "75%": "78.0",
          "100%": "83.0",
          "125%": "83.0",
          "150%": "81.0",
          "S.F.": null
        },
        "Efficiency": {
          "Rated Load": "0.0",
          "0%": "84.9",
          "25%": "89.6",
          "50%": "90.5",
          "75%": "89.6",
          "100%": "88.5",
          "125%": "87.0",
          "150%": "88.9",
          "S.F.": null
        },
        "Speed (RPM)": {
          "Rated Load": "1,799",
          "0%": "1,789",
          "25%": "1,776",
          "50%": "1,762",
          "75%": "1,750",
          "100%": "1,733",
          "125%": "1,714",
          "150%": "1,740",
          "S.F.": null
        },
        "Line Amps": {
          "Rated Load": "6.48",
          "0%": "7.10",
          "25%": "8.62",
          "50%": "10.86",
          "75%": "13.30",
          "100%": "15.88",
          "125%": "19.28",
          "150%": "14.80",
          "S.F.": null
        }
      },
      "performance_curves": {
        "image_url": "https://www.baldorvip.com/Drawing/ACPerformance?productNumber=CEBM3615T-D&recordId=93277"
      }
    }
  },
  "parts": [
    {
      "part_number": "36GS1000SP",
      "description": "GASKET-CONDUIT BOX, .06 THICK #SV-330 LE",
      "quantity": "1.000 EA"
    },
    {
      "part_number": "36FN3000C01SP",
      "description": "EXFN, PLASTIC, 5.25 OD, .912 ID",
      "quantity": "1.000 EA"
    },
    {
      "part_number": "LB1624",
      "description": "COMBINED WARNING LABEL, ISO/ANSI PICTOGR",
      "quantity": "1.000 EA"
    },
    {
      "part_number": "MN416A01",
      "description": "TAG-INSTAL-MAINT no wire (2400 bx)4/22",
      "quantity": "1.000 EA"
    }
  ]
}
```

Vou verificar se existe mais algum dado relevante, e se não existir, vou começar a organizar o json, para um formato parecido com o que foi pedido no arquivo do teste.
Finalizado a formatação do json, e o método para baixar os arquivos, ficou assim:
```json
{
    "url": "https://www.baldor.com/catalog/CEBM3615T-D",
    "code": "CEBM3615T-D",
    "description": "5HP, 1750RPM, 3PH, 60HZ, 184TC, 3642M, TEFC, F1",
    "info_packet_fileurl": "https://www.baldor.com/api/products/CEBM3615T-D/infopacket",
    "product_image_fileurl": "https://www.baldor.com/api/images/536",
    "ship_weight": "121.000 LB",
    "upc": "781568541739",
    "specs": {
        "Catalog Number": "CEBM3615T-D",
        "Enclosure": "TEFC",
        "Frame": "184TC",
        "Frame Material": "Steel",
        "Frequency": "60.00 Hz",
        "Motor Letter Type": "Three Phase",
        "Output @ Frequency": "5.000 HP @ 60 HZ",
        "Phase": "3",
        "Synchronous Speed @ Frequency": "1800 RPM @ 60 HZ",
        "Voltage @ Frequency": "460.0 V @ 60 HZ",
        "Haz Area Class and Group": null,
        "Haz Area Division": "Not Applicable",
        "Agency Approvals": "CURUSEEV",
        "Ambient Temperature": "40 °C",
        "Auxillary Box": "No Auxillary Box",
        "Auxillary Box Lead Termination": null,
        "Base Indicator": "Rigid",
        "Bearing Grease Type": "Polyrex EM (-20F +300F)",
        "Blower": null,
        "Brake Torque": "25.0 lb-ft",
        "Current @ Voltage": "13.900 A @ 208.0 V",
        "Design Code": "B",
        "Drip Cover": "No Drip Cover",
        "Duty Rating": "CONT",
        "Efficiency @ 100% Load": "89.5 %",
        "Electrically Isolated Bearing": "Not Electrically Isolated",
        "Feedback Device": "NO FEEDBACK",
        "High Voltage Full Load Amps": "6.7 a",
        "Front Face Code": "Fan Housing Cover For Brake",
        "Front Shaft Indicator": null,
        "Heater Indicator": "No Heater",
        "Insulation Class": "F",
        "Inverter Code": "Inverter Ready",
        "KVA Code": "J",
        "Lifting Lugs": "Standard Lifting Lugs",
        "Locked Bearing Indicator": "Locked Bearing",
        "Motor Lead Exit": "Ko Box",
        "Motor Lead Termination": "Flying Leads",
        "Motor Lead Quantity/Wire Size": "9 @ 16 AWG",
        "Motor Type": "3642M",
        "Mounting Arrangement": "F1",
        "Number of Poles": "4",
        "Overall Length": "23.13 IN",
        "Power Factor": "78",
        "Product Family": "General Purpose",
        "Product Type": "D-SERIES BRAKE MOTORS",
        "Pulley End Bearing Type": "Ball",
        "Pulley Face Code": "C-Face",
        "Pulley Shaft Indicator": "Standard",
        "Rodent Screen": null,
        "Service Factor": "1.15",
        "Shaft Diameter": "1.125 IN",
        "Shaft Extension Location": "Pulley End",
        "Shaft Ground Indicator": "No Shaft Grounding",
        "Shaft Rotation": "Reversible",
        "Shaft Slinger Indicator": "No Slinger",
        "Speed": "1750 rpm",
        "Speed Code": "Single Speed",
        "Motor Standards": "NEMA",
        "Starting Method": "Direct on line",
        "Thermal Device - Bearing": null,
        "Thermal Device - Winding": null,
        "Vibration Sensor Indicator": "No Vibration Sensor",
        "Winding Thermal 1": null,
        "Winding Thermal 2": null
    },
    "cad_files": [
        {
            "name": "2D AutoCAD DWG >=2000",
            "value": "36LYM650_23.14.DWG",
            "version": "",
            "filetype": "2D",
            "cad_36LYM650_23.14.DWG_fileurl": "https://www.baldor.com/api/products/download/?value=36LYM650_23.14.DWG&url=http%3A%2F%2FUSFSM-S-HQDMS02.baldor.abb.com%3A1090%2FContentServer%2FContentServer.dll%3Fget%26pVersion%3D0046%26contRep%3DZMARKETING%26docId%3D02063300001C1EE58196499E4069BE98%26compId%3D36LYM650_23.14.DWG"
        },
        {
            "name": "2D AutoCAD DXF >=2000",
            "value": "36LYM650_23.14.DXF",
            "version": "",
            "filetype": "2D",
            "cad_36LYM650_23.14.DXF_fileurl": "https://www.baldor.com/api/products/download/?value=36LYM650_23.14.DXF&url=http%3A%2F%2FUSFSM-S-HQDMS02.baldor.abb.com%3A1090%2FContentServer%2FContentServer.dll%3Fget%26pVersion%3D0046%26contRep%3DZMARKETING%26docId%3D02063300001C1EE58196499E406ADE98%26compId%3D36LYM650_23.14.DXF"
        },
        {
            "name": "3D ACIS",
            "value": "36LYM650_23.14.sat",
            "version": "",
            "filetype": "3D",
            "cad_36LYM650_23.14.sat_fileurl": "https://www.baldor.com/api/products/download/?value=36LYM650_23.14.sat&url=http%3A%2F%2FUSFSM-S-HQDMS02.baldor.abb.com%3A1090%2FContentServer%2FContentServer.dll%3Fget%26pVersion%3D0046%26contRep%3DZMARKETING%26docId%3D02063300000C1EE581965947E4DA9254%26compId%3D36LYM650_23.14.sat"
        },
        {
            "name": "3D Catia",
            "value": "36LYM650_23.14.cgr",
            "version": "",
            "filetype": "3D",
            "cad_36LYM650_23.14.cgr_fileurl": "https://www.baldor.com/api/products/download/?value=36LYM650_23.14.cgr&url=http%3A%2F%2FUSFSM-S-HQDMS02.baldor.abb.com%3A1090%2FContentServer%2FContentServer.dll%3Fget%26pVersion%3D0046%26contRep%3DZMARKETING%26docId%3D02063300000C1EE5819659734E341254%26compId%3D36LYM650_23.14.cgr"
        },
        {
            "name": "3D IGES",
            "value": "36LYM650_23.14.IGS",
            "version": "",
            "filetype": "3D",
            "cad_36LYM650_23.14.IGS_fileurl": "https://www.baldor.com/api/products/download/?value=36LYM650_23.14.IGS&url=http%3A%2F%2FUSFSM-S-HQDMS02.baldor.abb.com%3A1090%2FContentServer%2FContentServer.dll%3Fget%26pVersion%3D0046%26contRep%3DZMARKETING%26docId%3D02063300000C1EE5819656DDDDF23254%26compId%3D36LYM650_23.14.IGS"
        },
        {
            "name": "3D Parasolid X_B",
            "value": "36LYM650_23.14.x_b",
            "version": "",
            "filetype": "3D",
            "cad_36LYM650_23.14.x_b_fileurl": "https://www.baldor.com/api/products/download/?value=36LYM650_23.14.x_b&url=http%3A%2F%2FUSFSM-S-HQDMS02.baldor.abb.com%3A1090%2FContentServer%2FContentServer.dll%3Fget%26pVersion%3D0046%26contRep%3DZMARKETING%26docId%3D02063300000C1EE58196581C019A9254%26compId%3D36LYM650_23.14.x_b"
        },
        {
            "name": "3D SOLIDWORKS 2014",
            "value": "36LYM650_23.14.sldprt",
            "version": "",
            "filetype": "3D",
            "cad_36LYM650_23.14.sldprt_fileurl": "https://www.baldor.com/api/products/download/?value=36LYM650_23.14.sldprt&url=http%3A%2F%2FUSFSM-S-HQDMS02.baldor.abb.com%3A1090%2FContentServer%2FContentServer.dll%3Fget%26pVersion%3D0046%26contRep%3DZMARKETING%26docId%3D02063300001C1EE58196499E40689E98%26compId%3D36LYM650_23.14.sldprt"
        },
        {
            "name": "3D STEP",
            "value": "36LYM650_23.14.STEP",
            "version": "",
            "filetype": "3D",
            "cad_36LYM650_23.14.STEP_fileurl": "https://www.baldor.com/api/products/download/?value=36LYM650_23.14.STEP&url=http%3A%2F%2FUSFSM-S-HQDMS02.baldor.abb.com%3A1090%2FContentServer%2FContentServer.dll%3Fget%26pVersion%3D0046%26contRep%3DZMARKETING%26docId%3D02063300000C1EE5819657D6C8BAD254%26compId%3D36LYM650_23.14.STEP"
        }
    ],
    "drawings": [
        {
            "number": "36LYM650",
            "kind": "Dimension Sheet",
            "drawing_36LYM650_fileurl": "https://www.baldor.com/api/products/CEBM3615T-D/drawings/36LYM650",
            "kind_id": 0,
            "material": null,
            "description": null,
            "url": null,
            "type": null,
            "revision": null
        },
        {
            "number": "CD0005",
            "kind": "Connection Diagram",
            "drawing_CD0005_fileurl": "https://www.baldor.com/api/products/CEBM3615T-D/drawings/CD0005",
            "kind_id": 1,
            "material": null,
            "description": null,
            "url": null,
            "type": null,
            "revision": null
        },
        {
            "number": "CD2120",
            "kind": "Connection Diagram",
            "drawing_CD2120_fileurl": "https://www.baldor.com/api/products/CEBM3615T-D/drawings/CD2120",
            "kind_id": 1,
            "material": null,
            "description": null,
            "url": null,
            "type": null,
            "revision": null
        }
    ],
    "nameplate": {
        "CAT.NO.": "CEBM3615T-D",
        "SPEC.": "36M650S268G1",
        "HP": "5",
        "VOLTS": "230/460",
        "AMP": "13.4/6.7",
        "RPM": "1750",
        "FRAME": "184TC",
        "HZ": "60",
        "PH": "3",
        "SER.F.": "1.15",
        "CODE": "J",
        "DES": "B",
        "CL": "F",
        "NEMA-NOM-EFF": "89.5",
        "PF": "78",
        "RATING": "40C AMB-CONT",
        "CC": "010A",
        "DE": "6206",
        "ODE": "6205",
        "ENCL": "TEFC"
    },
    "performance": {
        "460 V, 60 Hz, 5 hp": {
            "general_characteristics": {
                "Full Load Torque": "0 LB-FT",
                "No-Load Current": "0 A",
                "Line-Line Res. @ 25° C": "2.27 Ohms A Ph / 0 Ohms B Ph",
                "Temp. Rise @ Rated Load": "71° C",
                "Temp. Rise @ S.F. Load": "87° C",
                "Start Configuration": "DOL",
                "Break-Down Torque": "52.2 LB-FT",
                "Pull-Up Torque": "31.5 LB-FT",
                "Locked-Rotor Torque": "34.9 LB-FT",
                "Starting Current": "49.1 A"
            },
            "load_characteristics": {
                "Power Factor": {
                    "Rated Load": "6.0",
                    "0%": "39.0",
                    "25%": "60.0",
                    "50%": "72.0",
                    "75%": "78.0",
                    "100%": "83.0",
                    "125%": "83.0",
                    "150%": "81.0",
                    "S.F.": null
                },
                "Efficiency": {
                    "Rated Load": "0.0",
                    "0%": "85.0",
                    "25%": "89.7",
                    "50%": "90.6",
                    "75%": "89.6",
                    "100%": "88.6",
                    "125%": "87.0",
                    "150%": "89.0",
                    "S.F.": null
                },
                "Speed (RPM)": {
                    "Rated Load": "1,799",
                    "0%": "1,789",
                    "25%": "1,776",
                    "50%": "1,762",
                    "75%": "1,750",
                    "100%": "1,733",
                    "125%": "1,714",
                    "150%": "1,740",
                    "S.F.": null
                },
                "Line Amps": {
                    "Rated Load": "3.24",
                    "0%": "3.55",
                    "25%": "4.31",
                    "50%": "5.43",
                    "75%": "6.65",
                    "100%": "7.94",
                    "125%": "9.64",
                    "150%": "7.42",
                    "S.F.": null
                }
            },
            "performance_curves": {
                "performance_curves_fileurl": "https://www.baldorvip.com/Drawing/ACPerformance?productNumber=CEBM3615T-D&recordId=35063"
            }
        },
        "230 V, 60 Hz, 5 hp": {
            "general_characteristics": {
                "Full Load Torque": "0 LB-FT",
                "No-Load Current": "0 A",
                "Line-Line Res. @ 25° C": "0.567 Ohms A Ph / 0 Ohms B Ph",
                "Temp. Rise @ Rated Load": "71° C",
                "Temp. Rise @ S.F. Load": "86° C",
                "Start Configuration": "DOL",
                "Break-Down Torque": "52.2 LB-FT",
                "Pull-Up Torque": "31.5 LB-FT",
                "Locked-Rotor Torque": "34.9 LB-FT",
                "Starting Current": "98.2 A"
            },
            "load_characteristics": {
                "Power Factor": {
                    "Rated Load": "6.0",
                    "0%": "38.0",
                    "25%": "60.0",
                    "50%": "72.0",
                    "75%": "78.0",
                    "100%": "83.0",
                    "125%": "83.0",
                    "150%": "81.0",
                    "S.F.": null
                },
                "Efficiency": {
                    "Rated Load": "0.0",
                    "0%": "84.9",
                    "25%": "89.6",
                    "50%": "90.5",
                    "75%": "89.6",
                    "100%": "88.5",
                    "125%": "87.0",
                    "150%": "88.9",
                    "S.F.": null
                },
                "Speed (RPM)": {
                    "Rated Load": "1,799",
                    "0%": "1,789",
                    "25%": "1,776",
                    "50%": "1,762",
                    "75%": "1,750",
                    "100%": "1,733",
                    "125%": "1,714",
                    "150%": "1,740",
                    "S.F.": null
                },
                "Line Amps": {
                    "Rated Load": "6.48",
                    "0%": "7.10",
                    "25%": "8.62",
                    "50%": "10.86",
                    "75%": "13.30",
                    "100%": "15.88",
                    "125%": "19.28",
                    "150%": "14.80",
                    "S.F.": null
                }
            },
            "performance_curves": {
                "performance_curves_fileurl": "https://www.baldorvip.com/Drawing/ACPerformance?productNumber=CEBM3615T-D&recordId=93277"
            }
        }
    },
    "parts": [
        {
            "part_number": "36GS1000SP",
            "description": "GASKET-CONDUIT BOX, .06 THICK #SV-330 LE",
            "quantity": "1.000 EA"
        },
        {
            "part_number": "36FN3000C01SP",
            "description": "EXFN, PLASTIC, 5.25 OD, .912 ID",
            "quantity": "1.000 EA"
        },
        {
            "part_number": "LB1624",
            "description": "COMBINED WARNING LABEL, ISO/ANSI PICTOGR",
            "quantity": "1.000 EA"
        },
        {
            "part_number": "MN416A01",
            "description": "TAG-INSTAL-MAINT no wire (2400 bx)4/22",
            "quantity": "1.000 EA"
        }
    ],
    "assets": {
        "image": "assets/CEBM3615T-D/img.jpg",
        "infopacket": "assets/CEBM3615T-D/infopacket.pdf",
        "cad": "assets/CEBM3615T-D/cad.STEP",
        "drawing_36LYM650": "assets/CEBM3615T-D/drawing_36LYM650.pdf",
        "drawing_CD0005": "assets/CEBM3615T-D/drawing_CD0005.pdf",
        "drawing_CD2120": "assets/CEBM3615T-D/drawing_CD2120.pdf",
        "performance_curves_460 V, 60 Hz, 5 hp": "assets/CEBM3615T-D/performance_curves_460 V, 60 Hz, 5 hp.pdf",
        "performance_curves_230 V, 60 Hz, 5 hp": "assets/CEBM3615T-D/performance_curves_230 V, 60 Hz, 5 hp.pdf"
    }
}
```


Feito isso agora é implementar um código para buscar os produtos no site. Eu encontrei o arquivo sitemap.xml contendo todas as páginas dos produtos, seria interessante buscar por ele, só que como você deve ter reparado, no nosso json atual um campo está faltando, o nome do produto, só temos acesso ao código. E para isso eu preciso acessar o site diretamente. Baseado no que eu naveguei pelo site, podemos usar as seguintes chamadas a api, que são públicas, e a primeira vista, não contém nenhum tipo de proteção. Encontrei este fluxo, e vou me basear para criar um crawler a partir dele:

PS (Este foi o sitemap que encontrei atráves do arquivo "robots.txt": http://www.baldor.com/mvc/sitemap/products)

List all categories of products
https://www.baldor.com/api/products?include=results&language=en-US&include=filters&include=category&pageSize=10

List all types of products in the category:
https://www.baldor.com/api/products?include=results&language=en-US&include=filters&include=category&pageSize=10&category=2

List all products with the selected type and category:
https://www.baldor.com/api/products?include=results&language=en-US&include=filters&include=category&pageSize=10&category=69

Com isso teremos acessos a todos os ids de produtos, tipos e categorias. Após extrair os ids, basta extrair usando nosso método criado até aqui.

Criei um arquivo chamado crawler.py que vai puxar todas as categorias -> subcategorias -> produtos usando o fluxo mencionado anteriormente, adicionei um limite variável popis como citado no teste não é necessário extrair todos os produtos do site. Poderia tornar o código mais modular, para escoher de qual categoria ou subcategoria deseja extrair os produtos, etc. Mas com intuito de entregar o projeto com velocidade legal, vou enviar o necessário e focar em outras partes.

Adicionei threads no main.py para acelerar o processo de extração.

Adicionei docker para facilitar quem for executar o teste, instruções para rodar estão no arquivo README.md.