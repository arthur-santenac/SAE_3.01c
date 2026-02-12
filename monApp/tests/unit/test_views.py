import io

def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Importer" in response.data

def test_upload_sans_fichier(client):
    response = client.post("/importe_csv/")
    assert response.status_code == 400
    assert b"Aucun fichier" in response.data

def test_upload_mauvaise_extension(client):
    data = {
        'file': (io.BytesIO(b"contenu"), 'image.jpg')
    }
    response = client.post("/importe_csv/", data=data, content_type='multipart/form-data')
    assert b"configuration" not in response.data.lower()

def test_complet(client):
    csv = (
        "num,nom,prenom,Genre,Niveau Maths\n"
        "1,Nom1,Prenom1,M,1\n"
        "2,Nom2,Prenom2,F,1\n"
        "3,Nom3,Prenom3,M,2\n"
        "4,Nom4,Prenom4,F,2"
    ).encode('utf-8')
    
    data = {
        'file': (io.BytesIO(csv), 'test.csv')
    }
    
    response_upload = client.post(
        "/importe_csv/", 
        data=data, 
        content_type='multipart/form-data',
        follow_redirects=True
    )
    assert response_upload.status_code == 200
    assert b"configuration" in response_upload.data.lower()
    data1 = {
        "btn": "btn-valide",
        "nb-grp": "2",
        "importance_Genre": "50",
        "importance_Niveau": "50"
    }
    response1 = client.post("/configuration/", data=data1, follow_redirects=True)
    assert response1.status_code == 200
    assert b"Groupe 1" in response1.data

    data2 = {
        "btn": "btn-repartition",
        "nb-grp": "2",
        "chk_1_Genre": "M", 
        "chk_2_Genre": "F"
    }
    response2 = client.post("/configuration/", data=data2, follow_redirects=True)
    assert response2.status_code == 200

    assert b"score" in response2.data.lower() or b"Relancer" in response2.data

def test_exporter_groupes_success(client):
    data = {
        "liste_critere": ["Genre", "Niveau Maths"],
        "groupes": [
            [
                {"num": "1", "nom": "Nom1", "prenom": "Prenom1", "criteres": {"Genre": "M", "Niveau Maths": "1"}}
            ],
            [
                {"num": "2", "nom": "Nom2", "prenom": "Prenom2", "criteres": {"Genre": "F", "Niveau Maths": "2"}}
            ]
        ]
    }
    response = client.post("/exporter_groupes", json=data)
    assert response.status_code == 200
    assert response.headers["Content-Disposition"].startswith("attachment")
    assert response.mimetype == "text/csv"
    content = response.data.decode("utf-8")
    assert "num,nom,prenom,Genre,Niveau Maths,groupe" in content
    assert "1,Nom1,Prenom1,M,1,1" in content
    assert "2,Nom2,Prenom2,F,2,2" in content

def test_exporter_groupes_sans_data(client):
    response = client.post("/exporter_groupes", json={})
    assert response.status_code == 400
    assert b"manquantes" in response.data

def test_calculer_stats(client):
    data = {
        "dico_importance": {"Genre": 50, "Niveau Maths": 50},
        "groupes": [
            [
                {"criteres": {"Genre": "M", "Niveau Maths": "1"}}
            ],
            [
                {"criteres": {"Genre": "F", "Niveau Maths": "2"}}
            ],
            [
                {"criteres": {"Genre": "M", "Niveau Maths": "2"}}
            ]
        ]
    }

    response = client.post("/api/calculer_stats", json=data)

    assert response.status_code == 200
    json_resp = response.get_json()

    assert json_resp["success"] is True
    assert "score" in json_resp
    assert isinstance(json_resp["score"], int)
    assert json_resp["place_text"] == "2/3"
    assert 66 < json_resp["prc_place"] < 67
    assert json_resp["is_complete"] is False

def test_calculer_stats_complet(client):
    data = {
        "dico_importance": {"Genre": 100},
        "groupes": [
            [{"criteres": {"Genre": "M"}}],
            []
        ]
    }

    response = client.post("/api/calculer_stats", json=data)
    assert response.status_code == 200
    json_rep = response.get_json()
    assert json_rep["place_text"] == "1/1"
    assert json_rep["prc_place"] == 100
    assert json_rep["is_complete"] is True

def test_calculer_stats_error(client):
    data = {
        "groupes": "error" 
    }
    response = client.post("/api/calculer_stats", json=data)
    assert response.status_code == 500
    rep = response.get_json()
    assert rep["success"] is False
    assert "error" in rep
    
def test_json(client):
    data = {
        'file': (io.BytesIO(b'{}'), 'test.json')
    }
    response = client.post("/importer_json/", data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b"configuration" in response.data

def test_json_manquant(client):
    response = client.post("/importer_json/")
    assert response.status_code == 400
    assert b"Aucun fichier" in response.data

def test_json_mauvais_format(client):
    data = {
        'file': (io.BytesIO(b'contenu'), 'test.txt')
    }
    response = client.post("/importer_json/", data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b"Format invalide" in response.data