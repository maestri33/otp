"""CRUD end-to-end do recurso Item."""

from httpx import AsyncClient


async def test_create_and_get_item(client: AsyncClient) -> None:
    resp = await client.post("/items", json={"name": "Foo", "description": "bar"})
    assert resp.status_code == 201
    item = resp.json()
    assert item["name"] == "Foo"
    item_id = item["id"]

    resp = await client.get(f"/items/{item_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == item_id


async def test_get_item_not_found(client: AsyncClient) -> None:
    resp = await client.get("/items/99999")
    assert resp.status_code == 404
    assert resp.json()["code"] == "not_found"


async def test_list_update_delete(client: AsyncClient) -> None:
    created = (await client.post("/items", json={"name": "A"})).json()
    iid = created["id"]

    resp = await client.get("/items")
    assert resp.status_code == 200
    assert any(i["id"] == iid for i in resp.json())

    resp = await client.patch(f"/items/{iid}", json={"name": "B"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "B"

    resp = await client.delete(f"/items/{iid}")
    assert resp.status_code == 204

    resp = await client.get(f"/items/{iid}")
    assert resp.status_code == 404
