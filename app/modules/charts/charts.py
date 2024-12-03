import matplotlib
matplotlib.use('Agg')  # Usa el backend 'Agg' para evitar problemas con tkinter
import matplotlib.pyplot as plt
import io
import base64

#Gráfico para los datasets con más descargas
def plot_downloads_bar_chart(dataset_names, download_counts):
    plt.figure(figsize=(10, 6))
    plt.bar(dataset_names, download_counts, color='skyblue')
    plt.title('Top 5 Datasets con Más Descargas', fontsize=16)
    plt.xlabel('Dataset', fontsize=14)
    plt.ylabel('Descargas', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()  # Cierra la figura para evitar consumo excesivo de memoria
    return plot_url


#Gráfico para los usuarios con más descargas
def plot_users_with_most_downloads(user_emails, download_counts):
    plt.figure(figsize=(10, 6))
    plt.bar(user_emails, download_counts, color='skyblue')
    plt.title('Top 5 Usuarios con más Dataets descargados', fontsize=16)
    plt.xlabel('Usuario', fontsize=14)
    plt.ylabel('Descargas', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()  # Cierra la figura para evitar consumo excesivo de memoria
    return plot_url


#Gráfico para las descargas de feature models
def plot_feature_models_with_most_downloads(feature_model_names, download_counts):
    plt.figure(figsize=(10, 6))
    plt.bar(feature_model_names, download_counts, color='skyblue')
    plt.title('Top 5 Feature Models con más Descargas', fontsize=16)
    plt.xlabel('Feature Model', fontsize=14)
    plt.ylabel('Descargas', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()  # Cierra la figura para evitar consumo excesivo de memoria
    return plot_url