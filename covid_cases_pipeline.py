import pandas as pd
import os
from sqlalchemy import create_engine

#Delaware zipcodes
zipcodes = [19701, 19702, 19703, 19706, 19707, 19708, 19709, 19710, 19711, 19712, 19713, 19714, 19715, 19716,
            19717, 19718, 19720, 19721, 19725, 19726, 19730, 19731, 19732, 19733, 19734, 19735, 19736, 19801,
            19802, 19803, 19804, 19805, 19806, 19807, 19808, 19809, 19810, 19850, 19880, 19884, 19885, 19886,
            19887, 19889, 19890, 19891, 19892, 19893, 19894, 19895, 19896, 19897, 19898, 19899, 19901, 19902,
            19903, 19904, 19905, 19906,19930, 19931, 19933, 19934, 19936, 19938, 19939, 19940, 19941, 19943,
            19944, 19945, 19946, 19947, 19950, 19951, 19952, 19953, 19954, 19955, 19956, 19958, 19960, 19961,
            19962, 19963, 19964, 19966, 19967, 19968, 19969, 19970, 19971, 19973, 19975, 19977, 19979, 19980]

#population by zipcode
zip_pop ={19720:59664, 19702:55537, 19711:52547, 19709:42480, 19701:40173, 19808:38657, 19805:38457, 19904:37467,
          19901:37182, 19713:30260, 19966:29324, 19958:26235, 19810:25978, 19802:25715, 19977:25670, 19973:24745,
          19803:21867, 19963:20743, 19947:19992, 19804:17511, 19801:17035, 19707:15821, 19703:15362, 19809:15139,
          19956:15117, 19934:13748, 19971:13739, 19734:13115, 19943:12887, 19962:11710, 19968:11659, 19933:10903,
          19952:10094, 19806:9887, 19975:9661, 19938:8856, 19970:8505, 19807:7515, 19950:7453, 19939:7399, 19945:6771,
          19960:6505, 19940:5575, 19946:5294, 19953:4545, 19717:3868, 19941:3270, 19930:2300, 19951:2103, 19706:1803,
          19954:1523, 19716:1429, 19967:1246, 21912:1139, 19964:1136, 19730:1100, 19979:719, 19944:697, 19731:322, 19936:319,
          19931:309, 19902:300, 19733:89, 19732:88, 19736:66, 19955:53, 19735:9}

#latitudes and longitudes by zipcode
lats_longs = {'19980':[39.07027,-75.57057],'19902':[39.128739445057505, -75.48659261372777],'19947':[38.676552,-75.39269],'19733':[39.555794,-75.65058],
'19971':[38.711512,-75.09677],'19706':[39.573744,-75.59204],'19951':[38.682345,-75.23286],'19901':[39.16426,-75.51163],'19966':[38.601355,-75.2411],
'19903':[39.10868,-75.448023],'19808':[39.734279,-75.6631],'19930':[38.536354,-75.06062],'19711':[39.700561,-75.7431],'19810':[39.817645,-75.50242],
'19904':[39.161639,-75.5587],'19975':[38.463751,-75.15642],'19939':[38.557501,-75.21465],'19934':[39.094699,-75.58871],'19734':[39.386601,-75.66801],
'19950':[38.818541,-75.60966],'19931':[38.570238,-75.6147],'19940':[38.469655,-75.5669],'19943':[39.011387,-75.58978],'19809':[39.771663,-75.49656],
'19977':[39.29799,-75.59391],'19807':[39.787512,-75.60256],'19967':[38.54597,-75.11175],'19709':[39.479602,-75.6932],'19736':[39.80834295411041, -75.67435944928607],
'19703':[39.800945,-75.46455],'19979':[39.0461,-75.57185],'19717':[39.67847598234869, -75.75109424476862],'19701':[39.598203,-75.69945],'19806':[39.758563,-75.56413],
'19968':[38.772648,-75.28665],'19964':[39.098772,-75.73943],'19970':[38.55044,-75.09928],'19944':[38.459314,-75.05356],'19938':[39.265066,-75.6807],'19973':[38.643248,-75.61102],
'19956':[38.549721,-75.55304],'19803':[39.793962,-75.53401],'19936':[39.218448,-75.584848],'19801':[39.738563,-75.54833],'19710':[39.79433637618826, -75.58848998207941],
'19732':[39.78490897774897, -75.56850477797175],'19731':[39.52183455625439, -75.58434777016139],'19960':[38.855872,-75.39889],'19707':[39.784014,-75.68586],
'19952':[38.916908,-75.61343],'19735':[39.80978121868842, -75.60444217572372],'19804':[39.721062,-75.60806],'19933':[38.73635,-75.60807],'19963':[38.922806,-75.41449],
'19730':[39.456484,-75.65976],'19802':[39.756213,-75.53312],'19946':[39.037803,-75.46634],'19962':[39.06517,-75.49858],'19958':[38.746207,-75.16282],
'19955':[39.22618213687513, -75.66814007775329],'19702':[39.626297,-75.71386], '19954':[38.909621,-75.51264],'19716':[39.68906977042565, -75.75744085892133],
'19805':[39.745377,-75.58251],'19941':[38.80136,-75.42595],'19720':[39.669219,-75.59003], '19945':[38.511469,-75.18364], '19713':[39.669211,-75.71796],'19953':[39.150822,-75.70428]}

#connect to database
url = os.getenv('URL')
engine = create_engine(url)
con = engine.connect()

def get_data():
    li = []
    no_data_to_show = []
    for zipcode in zipcodes:
        url = 'https://myhealthycommunity.dhss.delaware.gov/locations/zip-code-' + str(
            zipcode) + '/download_covid_19_data/cases'
        try:
            df = pd.read_csv(url)
            li.append(df)

        except pd.errors.ParserError:
            no_data_to_show.append(zipcode)

        df = pd.concat(li, axis=0, ignore_index=True)

    # convert location to int zipcodes and rename column
    df['Location'] = df['Location'].apply(lambda x: int(str(x[9::])))
    df.rename(columns={'Location': 'Zipcode'}, inplace=True)

    # add population column
    df['Zipcode Population'] = df['Zipcode'].map(zip_pop)

    # add new date column and drop Month, Day and Year Columns
    df.replace({'Month': {1: '01', 2: '02', 3: '03', 4: '04', 5: '05', 6: '06', 7: '07', 8: '08', 9: '09'},
                'Day': {1: '01', 2: '02', 3: '03', 4: '04', 5: '05', 6: '06', 7: '07', 8: '08', 9: '09'}}, inplace=True)

    df['Date'] = df['Year'].apply(str) + df['Month'].apply(str) + df['Day'].apply(str)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
    df = df.drop(['Day', 'Month', 'Year'], axis=1)

    # add zipcode date which will serve as the primary key}
    df['Zipcode Date'] = df['Zipcode'].astype(str) + " " + df['Date'].astype(str)

    #add latitude and lungitude columns
    lats = dict()
    longs = dict()
    for key, value in lats_longs.items():
        lats[int(key)] = float(value[0])
        longs[int(key)] = float(value[1])
    df['Zipcode latitude'] = df['Zipcode'].map(lats)
    df['Zipcode longitude'] = df['Zipcode'].map(longs)

    #add to temp table in database
    df.to_sql('covid_cases_temp', con, if_exists='replace', index=False)
    #transfer from temptable to main table in database
    con.execute("INSERT IGNORE INTO covid_cases SELECT * FROM covid_cases_temp")

if __name__ == "__main__":
    get_data()


