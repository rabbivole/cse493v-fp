using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlayerController : MonoBehaviour
{
    [SerializeField] Transform resetTo;
    [SerializeField] GameObject player;
    [SerializeField] Camera playerHead;

    [ContextMenu("Reset Position")] 
    public void ResetPosition()
    {
        float rotationAngleY = playerHead.transform.rotation.eulerAngles.y - resetTo.transform.rotation.eulerAngles.y;
        player.transform.Rotate(0, -rotationAngleY, 0);
        Debug.Log("rotY: ");
        Debug.Log(-rotationAngleY);

        Vector3 distanceDiff = resetTo.position - playerHead.transform.position;
        player.transform.position += distanceDiff;
        Debug.Log(distanceDiff);
    }
}
