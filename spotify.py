import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import io
import matplotlib.pyplot as plt # type: ignore
import seaborn as sb # type: ignore

def load_data(file_uploaded):
    
    """Fonction pour charger le fichier CSV
    Args:
        uploaded_file (_type_): _description_

    Returns:
        _type_: _description_
        _type_: _description_
        _type_: _description_
    """

    try:
        df = pd.read_csv(file_uploaded, encoding='latin1')
        return df, None
    except Exception as ex:
        return None, str(ex)

def show_diagnostics(df):

    """Fonction pour afficher le diagnostic du fichier dans un onglet de l'app
    Args:
        df (_type_): _description_
    """

    st.write("### Dimensions du fichier")
    st.write(f"{df.shape[0]} lignes et {df.shape[1]} colonnes")

    # Permet d'afficher les informations sur le dataframe sauf que df.info() renvoie None donc on passe par une memoire tampon
    st.write("### Information sur le dataframe")
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    st.text(info_str)

    st.write("### Aperçu des premières lignes")
    st.dataframe(df.head())

    st.write("### Valeurs manquantes")
    missing_values = df.isnull().sum()
    st.dataframe(missing_values[missing_values > 0])

    st.write("### Duplications")
    duplicated = df.duplicated().sum()
    st.write(f"Nombre de lignes dupliquées : {duplicated}")

    st.write("### Types de données")
    st.dataframe(df.dtypes)

def show_cleaning(df):

    """Fonction pour nettoyer le fichier dans un onglet de l'app
    Args:
        df (_type_): _description_

    Returns:
        _type_: _description_
    """

    # Gestion des valeurs manquantes
    st.write("### Gestion des valeurs manquantes")
    before_lines = df.shape[0]
    df = df.dropna()
    after_lines = df.shape[0]
    st.success(f"{before_lines - after_lines} lignes à valeurs manquantes supprimées")

    # Clean des colonnes avec du texte 
    st.write("### Nettoyage des textes")
    text_cols = df.select_dtypes(include='object').columns
    for col in text_cols:
        df[col] = df[col].str.strip()
    st.success(f"{len(text_cols)} colonnes texte nettoyées")

    # Clean des colonnes numériques typé object 
    st.write("### Nettoyage des colonnes numériques")
    cols_to_convert = ['in_deezer_playlists', 'in_shazam_charts']
    for col in cols_to_convert:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", "").str.replace(" ", "").str.extract('(\d+\.?\d*)')[0]
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    col = 'streams'
    # Tente de convertir la colonne en numérique (les erreurs deviennent NaN)
    df[col] = pd.to_numeric(df[col], errors='coerce')
    # Supprime les lignes où la conversion a échoué (NaN)
    df = df.dropna(subset=[col])

    st.success(f"{len(cols_to_convert)+1} colonnes numériques nettoyées")


    st.write("### Fichier nettoyé : ")
    st.write("#### Information : ")
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    st.text(info_str)

    st.write("#### Valeurs manquantes")
    missing_values = df.isnull().sum()
    st.dataframe(missing_values[missing_values > 0])

    return df

def show_comparaison(df):
    """Fonction pour afficher la comparaison entre le nombre de morceaux et le pourcentage de streams"""

    total_tracks = len(df)
    solo_tracks = len(df[df['artist_count'] == 1])
    one_feat_tracks = len(df[df['artist_count'] == 2])
    two_feat_tracks = len(df[df['artist_count'] == 3])
    three_feat_tracks = len(df[df['artist_count'] == 4])

    solo_percentage = (solo_tracks / total_tracks) * 100
    one_feat_percentage = (one_feat_tracks / total_tracks) * 100
    two_feat_percentage = (two_feat_tracks / total_tracks) * 100
    three_feat_percentage = (three_feat_tracks / total_tracks) * 100

    solo_streams = df[df['artist_count'] == 1]['streams'].sum()
    one_feat_streams = df[df['artist_count'] == 2]['streams'].sum()
    two_feat_streams = df[df['artist_count'] == 3]['streams'].sum()
    three_feat_streams = df[df['artist_count'] == 4]['streams'].sum()

    total_streams = df['streams'].sum()
    solo_stream_percentage = (solo_streams / total_streams) * 100
    one_feat_stream_percentage = (one_feat_streams / total_streams) * 100
    two_feat_stream_percentage = (two_feat_streams / total_streams) * 100
    three_feat_stream_percentage = (three_feat_streams / total_streams) * 100

    solo_avg_streams = (solo_streams / solo_tracks) if solo_tracks > 0 else 0
    one_feat_avg_streams = (one_feat_streams / one_feat_tracks) if one_feat_tracks > 0 else 0

    st.write("##### Comparaison entre le nombre de morceaux et le pourcentage de strams")
    st.write(f"Pourcentage de morceaux seuls (1 artiste) : {solo_percentage:.2f}%")
    st.write(f"Moyenne des streams par morceau seul : {solo_avg_streams:,.0f}")
    st.write(f"Pourcentage des streams pour les morceaux seuls (1 artiste) : {solo_stream_percentage:.2f}%")
    st.write(f"Pourcentage de morceaux avec 1 feat (2 artistes) : {one_feat_percentage:.2f}%")
    st.write(f"Moyenne des streams par morceau avec 1 feat : {one_feat_avg_streams:,.0f}")
    st.write(f"Pourcentage des streams pour les morceaux avec 1 feat (2 artistes) : {one_feat_stream_percentage:.2f}%")
    st.write(f"Pourcentage de morceaux avec 2 feats (3 artistes) : {two_feat_percentage:.2f}%")
    st.write(f"Pourcentage des streams pour les morceaux avec 2 feats (3 artistes) : {two_feat_stream_percentage:.2f}%")
    st.write(f"Pourcentage de morceaux avec 3 feats (4 artistes) : {three_feat_percentage:.2f}%")
    st.write(f"Pourcentage des streams pour les morceaux avec 3 feats (4 artistes) : {three_feat_stream_percentage:.2f}%")

def show_analysis(df):

    """Fonction pour afficher l'analyse du fichier dans un onglet de l'app
    Args:
        df (_type_): _description_
    """

    # BPM
    if 'bpm' in df.columns:
        st.write("### Distribution du BPM")
        st.bar_chart(df['bpm'].value_counts().sort_index())

    # Key
    if 'key' in df.columns:
        st.write("### Distribution des tonalités (key)")
        st.bar_chart(df['key'].value_counts().sort_index())

    # Mode
    if 'mode' in df.columns:
        st.write("### Distribution des modes (majeur/mineur)")
        st.bar_chart(df['mode'].value_counts().sort_index())


    # Corrélations
    st.write("### Corrélations")

    #Artst count et streams
    corr = df['artist_count'].corr(df['streams'])
    st.write("##### Corrélation entre artist_count et streams")
    st.write(f"Corrélation : {corr:.2f}")
    fig, ax = plt.subplots()
    sb.scatterplot(data=df, x='artist_count', y='streams', ax=ax)
    st.pyplot(fig)

    # Comparaison
    show_comparaison(df)

    #Artst count et totale playlists et charts
    total_series = {
        "total_playlists": df['in_spotify_playlists'] + df['in_deezer_playlists'] + df['in_apple_playlists'],
        "total_charts": df['in_spotify_charts'] + df['in_apple_charts'] + df['in_deezer_charts'] + df['in_shazam_charts']
    }

    for label, series in total_series.items():
        st.write(f"##### Corrélation entre artist_count et {label}")
        corr = df['artist_count'].corr(series)
        st.write(f"Corrélation : {corr:.2f}")
        fig, ax = plt.subplots()
        sb.scatterplot(x=df['artist_count'], y=series, ax=ax)
        st.pyplot(fig)

    # Corrélation entre les streams et date de sortie globale
    df['release_date'] = pd.to_datetime(df['released_year'].astype(str) + '-' + df['released_month'].astype(str) + '-' + df['released_day'].astype(str))
    st.write("### Corrélation entre année de sortie (globale) et streams")
    corr = df['release_date'].dt.year.corr(df['streams'])
    st.write(f"Corrélation : {corr:.2f}")
    fig, ax = plt.subplots()
    sb.scatterplot(data=df, x=df['release_date'].dt.year, y='streams', ax=ax)
    st.pyplot(fig)
    
    # Corrélation entre les streams et date de sortie (2015-2023)
    df_filtre = df[(df['release_date'].dt.year >= 2015)]
    st.write("### Corrélation entre année de sortie (2015-2023) et streams")
    corr = df_filtre['release_date'].dt.year.corr(df_filtre['streams'])
    st.write(f"Corrélation : {corr:.2f}")
    fig, ax = plt.subplots()
    sb.scatterplot(data=df_filtre, x=df_filtre['release_date'].dt.year, y='streams', ax=ax)
    st.pyplot(fig)
    
    # Corrélation par mois et streams
    df['release_month'] = df['release_date'].dt.month
    st.write("### Corrélation entre mois de sortie et streams")
    corr_month = df['release_month'].corr(df['streams'])
    st.write(f"Corrélation mois : {corr_month:.2f}")
    fig, ax = plt.subplots()
    sb.scatterplot(data=df, x='release_month', y='streams', ax=ax)
    st.pyplot(fig)

    # Corrélation par jour et streams
    df['release_day'] = df['release_date'].dt.day
    st.write("### Corrélation entre jour de sortie et streams")
    corr_day = df['release_day'].corr(df['streams'])
    st.write(f"Corrélation jour : {corr_day:.2f}")
    fig, ax = plt.subplots()
    sb.scatterplot(data=df, x='release_day', y='streams', ax=ax)
    st.pyplot(fig)
    
    # Mois avec le plus de sorties
    df['release_month'] = df['release_date'].dt.month
    st.write("### Nombre de sorties par mois")
    monthly_counts = df['release_month'].value_counts().sort_index()
    fig, ax = plt.subplots()
    monthly_counts.plot(kind='bar', ax=ax)
    ax.set_title('Nombre de sorties par mois')
    ax.set_xlabel('Mois')
    ax.set_ylabel('Nombre de sorties')
    st.pyplot(fig)

    # Jours avec le plus de sorties
    df['release_day'] = df['release_date'].dt.day
    st.write("### Nombre de sorties par jour du mois")
    daily_counts = df['release_day'].value_counts().sort_index()
    fig, ax = plt.subplots()
    daily_counts.plot(kind='bar', ax=ax)
    ax.set_title('Nombre de sorties par jour du mois')
    ax.set_xlabel('Jour')
    ax.set_ylabel('Nombre de sorties')
    st.pyplot(fig)

    # Corrélation entre key, mode, BPM et playliste, charts
    for label, series in total_series.items():
        for col in ['key', 'mode']:
            st.write(f"##### Corrélation entre {col} et {label}")
            fig, ax = plt.subplots()
            sb.scatterplot(x=df[col], y=series, ax=ax)
            st.pyplot(fig)

        st.write(f"##### Corrélation entre BPM et {label}")
        corr = df['bpm'].corr(series)
        st.write(f"Corrélation : {corr:.2f}")
        fig, ax = plt.subplots()
        sb.scatterplot(x=df['bpm'], y=series, ax=ax)
        st.pyplot(fig)

    # Colonnes à analyser pour la suite
    columns_to_plot = ['speechiness_%', 'liveness_%', 'instrumentalness_%', 'acousticness_%', 'energy_%', 'valence_%', 'danceability_%']
    fig, axs = plt.subplots(4, 2, figsize=(15, 15))
    for i, column in enumerate(columns_to_plot):
        sb.histplot(df[column], bins=20, color='blue', ax=axs[i // 2, i % 2])
        axs[i // 2, i % 2].set(title=f"{column}", xlabel=column)
    plt.tight_layout()
    st.pyplot(fig)

    # Heatmap des corrélations
    df['total_playlists'] = (df['in_spotify_playlists'] + df['in_deezer_playlists'] + df['in_apple_playlists'])
    df['total_charts'] = (df['in_spotify_charts'] + df['in_apple_charts'] + df['in_deezer_charts'] + df['in_shazam_charts'])
    cols_to_corr = ['artist_count', 'streams', 'bpm', 'speechiness_%', 'liveness_%', 'instrumentalness_%', 'acousticness_%', 'energy_%', 'valence_%', 'danceability_%', 'total_playlists', 'total_charts']
    corr_matrix = df[cols_to_corr].corr()
    st.write("### Heatmap des corrélations")
    fig, ax = plt.subplots(figsize=(10, 8))
    sb.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    st.pyplot(fig)

    # Corrélations entre artist_count et speechiness
    corr = df['artist_count'].corr(df['speechiness_%'])
    st.write("##### Corrélation entre artist_count et speechiness")
    st.write(f"Corrélation : {corr:.2f}")
    fig, ax = plt.subplots()
    sb.scatterplot(data=df, x='artist_count', y='speechiness_%', ax=ax)
    st.pyplot(fig)

    # Corrélations 
    for lin in ['total_playlists', 'total_charts', 'streams', 'bpm']:
        fig, axs = plt.subplots(4, 2, figsize=(15, 15))
        columns_to_plot = ['speechiness_%', 'liveness_%', 'instrumentalness_%', 'acousticness_%', 'energy_%', 'valence_%', 'danceability_%']

        for i, column in enumerate(columns_to_plot):
            ax = axs[i // 2, i % 2]
            sb.scatterplot(data=df, x=column, y=lin, ax=ax)
            ax.set_title(f"{column} vs {lin}")

        plt.tight_layout()
        st.pyplot(fig)

    # Camembert
    key_counts = df['key'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(key_counts, labels=key_counts.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    ax.set_title('Répartition des tonalités (Key)')
    plt.axis('equal')
    st.pyplot(fig)
    
    # Pourcentage des streams par key
    key_percentage = df.groupby('key')['streams'].sum() / df['streams'].sum() * 100
    fig, ax = plt.subplots()
    ax.pie(key_percentage, labels=key_percentage.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    ax.set_title('Pourcentage des Streams par Tonalité (Key)')
    plt.axis('equal')
    st.pyplot(fig)

    # Pourcentage des total_playlists par key
    key_playlist_percentage = df.groupby('key')['total_playlists'].sum() / df['total_playlists'].sum() * 100
    fig, ax = plt.subplots()
    ax.pie(key_playlist_percentage, labels=key_playlist_percentage.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    ax.set_title('Pourcentage des Playlists par Tonalité (Key)')
    plt.axis('equal')
    st.pyplot(fig)

    # Pourcentage des total_charts par key
    key_chart_percentage = df.groupby('key')['total_charts'].sum() / df['total_charts'].sum() * 100
    fig, ax = plt.subplots()
    ax.pie(key_chart_percentage, labels=key_chart_percentage.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    ax.set_title('Pourcentage des Charts par Tonalité (Key)')
    plt.axis('equal')
    st.pyplot(fig)

    # Moyenne stream par BPM
    bpm_counts = df['bpm'].value_counts()
    bpm_filtre = bpm_counts[bpm_counts > 12].index
    bpm_filtre = df[df['bpm'].isin(bpm_filtre)]
    bpm_streams_avg = bpm_filtre.groupby('bpm')['streams'].mean()
    fig, ax = plt.subplots(figsize=(10, 6))
    bpm_streams_avg.plot(kind='line', ax=ax, color='blue')
    ax.set_title('Moyenne des Streams par BPM (plus de 12 morceaux)')
    ax.set_xlabel('BPM')
    ax.set_ylabel('Moyenne des Streams')
    st.pyplot(fig)



# Fonction Principale de l'application
def main():
    st.title("Analyse du dataset spotify-2023.cvs")

    file_uploaded = st.file_uploader("Chargez le fichier", type="csv")

    if file_uploaded is not None:
        df, error = load_data(file_uploaded)
        if error != None:
            st.error(f"Erreur lors du chargement du fichier : {error}")
        else:
            # Le fichier et l'encodage sont bon
            tab1, tab2, tab3 = st.tabs(["Diagnostic du fichier", "Clean du fichier", "Analyse du fichier"])
            with tab1:
                st.header("Diagnostic des données")
                show_diagnostics(df)
            with tab2:
                st.header("Clean du fichier")
                df = show_cleaning(df)
            with tab3:
                st.header("Analyse des données")
                show_analysis(df)

    else:
        st.info("Veuillez charger un fichier CSV pour commencer.")

main()