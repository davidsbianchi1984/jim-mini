package app.jim.wear

import android.content.Context
import androidx.health.services.client.HealthServices
import androidx.health.services.client.MeasureCallback
import androidx.health.services.client.data.Availability
import androidx.health.services.client.data.DataPointContainer
import androidx.health.services.client.data.DataType
import androidx.health.services.client.data.DataTypeAvailability
import androidx.health.services.client.data.DeltaDataType
import kotlinx.coroutines.guava.await

/**
 * The wrist's own pulse, and the only reason a watch is different from a
 * small phone.
 *
 * Every other surface in this product borrows somebody else's reading. This
 * one takes it. That is the whole argument for the watch existing as a
 * target at all, and it is why this file is the shortest one that matters:
 * open the measure callback, hand each reading to [WearApi.pulse], stop
 * when the screen the person is looking at goes away.
 *
 *     asked     may JIM read my pulse
 *     mattered  is anything reading it
 *
 * ## Health Services, not SensorManager
 *
 * A hand-rolled `SensorManager` loop on Wear gets the doze rules wrong and
 * either burns the battery or stops reporting when the screen turns off,
 * silently. Health Services is the layer the platform actually exposes
 * heart rate through, it batches, and it tells you when the sensor cannot
 * read — which is a thing this app needs to say out loud rather than
 * mistake for a calm heart.
 *
 * ## The permission is asked here, not at launch
 *
 * `BODY_SENSORS` is requested at the moment somebody switches the wrist
 * monitor on. Never at launch: a permission asked before there is anything
 * to do with it is a permission somebody grants without a reason, and this
 * product's whole posture about monitors is that a switch means something
 * because it was thrown deliberately.
 */
class Wrist(context: Context) {

    private val client = HealthServices.getClient(context).measureClient

    /** Whether this watch can read a heart rate at all. Some cannot, and a
     *  face that offers a switch for a sensor that does not exist is a face
     *  that teaches people the product is broken. */
    suspend fun capable(): Boolean = runCatching {
        client.getCapabilitiesAsync().await()
            .supportedDataTypesMeasure.contains(DataType.HEART_RATE_BPM)
    }.getOrDefault(false)

    private var callback: MeasureCallback? = null

    /**
     * Start reporting.
     *
     * `onReading` gets every accepted beat-per-minute; `onUnavailable` gets
     * the moment the sensor stops being able to read — a watch pushed up a
     * sleeve, or off the wrist entirely. Both are reported, because "no
     * reading" and "a resting reading" look identical on a face that only
     * ever draws numbers.
     */
    fun start(onReading: (Int) -> Unit, onUnavailable: () -> Unit) {
        if (callback != null) return
        val cb = object : MeasureCallback {
            // Health Services gives this one an empty default body, which
            // is the wrong default for this product: registration fails on
            // a watch whose sensor is unavailable or whose permission was
            // withdrawn between the grant and the call, and the silent
            // version of that is a face that draws nothing while the
            // person waits for a number. Same reporting path as losing
            // contact mid-reading — from the wearer's side they are the
            // same fact, which is that nothing is being read.
            override fun onRegistrationFailed(throwable: Throwable) {
                onUnavailable()
            }

            override fun onAvailabilityChanged(
                dataType: DeltaDataType<*, *>,
                availability: Availability,
            ) {
                if (availability != DataTypeAvailability.AVAILABLE)
                    onUnavailable()
            }

            override fun onDataReceived(data: DataPointContainer) {
                // The last of the batch, not all of them. A batch is the
                // same wrist a few seconds apart, and posting six readings
                // for six seconds of one arm would make the day's history
                // look like six separate observations of a person.
                data.getData(DataType.HEART_RATE_BPM).lastOrNull()?.let {
                    val bpm = it.value.toInt()
                    if (bpm > 0) onReading(bpm)
                }
            }
        }
        callback = cb
        client.registerMeasureCallback(DataType.HEART_RATE_BPM, cb)
    }

    /** Stop. Called from the composable's teardown — the same rule the
     *  console learned when leaving a screen had to end its voices: a
     *  sensor left open by a screen nobody is on is a sensor nobody
     *  switched on. */
    suspend fun stop() {
        val cb = callback ?: return
        callback = null
        runCatching { client.unregisterMeasureCallbackAsync(
            DataType.HEART_RATE_BPM, cb).await() }
    }
}
