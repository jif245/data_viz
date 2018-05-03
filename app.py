from flask import Flask, Response
import altair as alt
import pandas as pd
import urllib.request, json

app = Flask(__name__, static_url_path='', static_folder='.')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

@app.route("/vis/<zipcode>")
def hello(zipcode):
    response = ''
    zipcode = str(zipcode)
    RESTAURANT_URL      = "https://raw.githubusercontent.com/hvo/datasets/master/nyc_restaurants_by_cuisine.json"
    data = json.loads(urllib.request.urlopen(RESTAURANT_URL).read().decode())
    df_zip = pd.DataFrame.from_dict([x['perZip'] for x in data])
    df_zip['cuisine'] = [x['cuisine'] for x in data]

    data1 = df_zip.loc[:, [zipcode, 'cuisine']].sort_values(by = [zipcode], ascending=False)[:25]

    if data1 is not None:
        response = createChart(data1, zipcode).to_json()

    return Response(response,
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
            }
        )

def createChart(data, zipcode):
    color_expression    = "(indexof(lower(datum.cuisine), search.term)>=0) || (highlight._vgsid_==datum._vgsid_)"
    color_condition     = alt.ConditionalPredicateValueDef(color_expression, "SteelBlue")
    highlight_selection = alt.selection_single(name="highlight", on="mouseover", empty="none")
    search_selection    = alt.selection_single(name="search", on="mouseover", empty="none", fields=["term"],
                                               bind=alt.VgGenericBinding('input'))

    barchart = alt.Chart(data)\
        .mark_bar(stroke="Black") \
        .encode(
            alt.X("{0}:Q".format(zipcode), axis=alt.Axis(title="total")),
            alt.Y('cuisine:O', sort=alt.SortField(field="total", op="argmax")),
            alt.ColorValue("LightGrey", condition=color_condition),
        ).properties(
            selection=(highlight_selection + search_selection),
        )
    return alt.hconcat(barchart,
        data=data,
        title="counts in zipcode: {}".format(zipcode)
    )

if __name__ == '__main__':
    app.run(port=8002)
