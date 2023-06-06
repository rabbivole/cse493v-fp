using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/**
 * Used for resetting head position. https://www.youtube.com/watch?v=EmjBonbATS0 
 * (and then I also looked at a few minutes of another tutorial he had on mapping button inputs)
 */

public class PlayerController : MonoBehaviour
{
    [SerializeField] Transform resetTo;
    [SerializeField] GameObject player;
    [SerializeField] Camera playerHead;

    [ContextMenu("Reset Position")] 
    public void ResetPosition()
    {
        // is there a reason why we do a transform here rather than more directly setting transform.rotation?
        // did he do it this way because quaternions are scary or am i just dumb
        float rotationAngleY = playerHead.transform.rotation.eulerAngles.y - resetTo.transform.rotation.eulerAngles.y;
        player.transform.Rotate(0, -rotationAngleY, 0);

        // in theory, we'd like to be a little smarter about this and not change the y value. 
        // i *think* head height is tracked fairly reasonably, it's mostly x/z position that are an issue
        // also not every user is hobbit height like i am
        Vector3 distanceDiff = resetTo.position - playerHead.transform.position;
        player.transform.position += distanceDiff;
    }
}
