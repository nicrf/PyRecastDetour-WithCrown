// Stub implementations for DebugUtils functions that we don't need

#include "include/recastnavigation/Recast.h"
#include "include/recastnavigation/RecastDump.h"

// Stub for duFileIO destructor
duFileIO::~duFileIO() {}

// Stub for duLogBuildTimes
void duLogBuildTimes(rcContext& /*ctx*/, int /*totalTimeUsec*/)
{
    // Do nothing - we don't need build time logging
}
